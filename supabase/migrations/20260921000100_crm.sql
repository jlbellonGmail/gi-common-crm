-- GI-COMMON-CRM tenant-aware schema (Leads).
-- Mismo patron que persons.*: la aplicacion debe SET LOCAL app.organization_id
-- en cada transaccion; RLS forzado es la defensa real, no una conveniencia.
-- search_path explicito en cada funcion (hardening equivalente al aplicado
-- despues del hecho en gi-common-persons/20260920000101_persons_hardening.sql,
-- incorporado aqui desde el origen).

create extension if not exists pgcrypto;
create schema if not exists crm;

create table if not exists crm.lead_source (
    organization_id text not null,
    source_id uuid not null default gen_random_uuid(),
    code text not null check (length(btrim(code)) between 1 and 80),
    label text not null check (length(btrim(label)) between 1 and 200),
    active boolean not null default true,
    created_at timestamptz not null default timezone('utc', now()),
    primary key (organization_id, source_id),
    unique (organization_id, code)
);

create table if not exists crm.lead (
    organization_id text not null,
    lead_id uuid not null default gen_random_uuid(),
    status text not null default 'new'
        check (status in ('new', 'contacted', 'qualified', 'in_progress', 'won', 'lost', 'archived')),
    person_id uuid,
    source_id uuid,
    owner_user_id text,
    title text not null check (length(btrim(title)) between 1 and 200),
    description text,
    close_reason text,
    version bigint not null default 1 check (version > 0),
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),
    primary key (organization_id, lead_id),
    foreign key (organization_id, source_id)
        references crm.lead_source (organization_id, source_id) on delete restrict
);

create table if not exists crm.lead_status_event (
    organization_id text not null,
    event_id uuid not null default gen_random_uuid(),
    lead_id uuid not null,
    from_status text,
    to_status text not null,
    actor_user_id text not null,
    occurred_at timestamptz not null default timezone('utc', now()),
    reason text,
    primary key (organization_id, event_id),
    foreign key (organization_id, lead_id)
        references crm.lead (organization_id, lead_id) on delete restrict
);

create table if not exists crm.lead_activity (
    organization_id text not null,
    activity_id uuid not null default gen_random_uuid(),
    lead_id uuid not null,
    actor_user_id text not null,
    kind text not null check (kind in ('note', 'call', 'email', 'meeting', 'other')),
    notes text not null default '',
    occurred_at timestamptz not null default timezone('utc', now()),
    primary key (organization_id, activity_id),
    foreign key (organization_id, lead_id)
        references crm.lead (organization_id, lead_id) on delete restrict
);

create table if not exists crm.lead_assignment_event (
    organization_id text not null,
    assignment_id uuid not null default gen_random_uuid(),
    lead_id uuid not null,
    from_user_id text,
    to_user_id text not null,
    actor_user_id text not null,
    occurred_at timestamptz not null default timezone('utc', now()),
    primary key (organization_id, assignment_id),
    foreign key (organization_id, lead_id)
        references crm.lead (organization_id, lead_id) on delete restrict
);

create table if not exists crm.lead_external_reference (
    organization_id text not null,
    reference_id uuid not null default gen_random_uuid(),
    lead_id uuid not null,
    vertical_code text not null check (length(btrim(vertical_code)) between 1 and 80),
    external_type text not null check (length(btrim(external_type)) between 1 and 80),
    external_id text not null check (length(btrim(external_id)) between 1 and 200),
    created_at timestamptz not null default timezone('utc', now()),
    primary key (organization_id, reference_id),
    foreign key (organization_id, lead_id)
        references crm.lead (organization_id, lead_id) on delete restrict,
    unique (organization_id, vertical_code, external_type, external_id)
);

create table if not exists crm.lead_audit (
    organization_id text not null,
    audit_id uuid not null default gen_random_uuid(),
    lead_id uuid,
    actor_user_id text not null,
    action text not null,
    occurred_at timestamptz not null default timezone('utc', now()),
    correlation_id text not null,
    outcome text not null,
    entity_version bigint,
    primary key (organization_id, audit_id),
    foreign key (organization_id, lead_id)
        references crm.lead (organization_id, lead_id) on delete restrict
);

create index if not exists lead_by_organization_status
    on crm.lead (organization_id, status, lead_id);
create index if not exists lead_by_organization_owner
    on crm.lead (organization_id, owner_user_id);
create index if not exists lead_by_organization_person
    on crm.lead (organization_id, person_id);
create index if not exists lead_status_event_by_lead
    on crm.lead_status_event (organization_id, lead_id, occurred_at desc);
create index if not exists lead_activity_by_lead
    on crm.lead_activity (organization_id, lead_id, occurred_at desc);
create index if not exists lead_assignment_by_lead
    on crm.lead_assignment_event (organization_id, lead_id, occurred_at desc);
create index if not exists lead_external_reference_by_lead
    on crm.lead_external_reference (organization_id, lead_id);
create index if not exists lead_audit_by_lead_time
    on crm.lead_audit (organization_id, lead_id, occurred_at desc);

grant usage on schema crm to authenticated;
grant select, insert, update on crm.lead_source to authenticated;
grant select, insert, update on crm.lead to authenticated;
grant select, insert on crm.lead_status_event to authenticated;
grant select, insert on crm.lead_activity to authenticated;
grant select, insert on crm.lead_assignment_event to authenticated;
grant select, insert on crm.lead_external_reference to authenticated;
grant select, insert on crm.lead_audit to authenticated;

create or replace function crm.touch_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
    new.updated_at = timezone('utc', now());
    return new;
end;
$$;

create or replace function crm.reject_append_only_mutation()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
    raise exception '% is append-only', tg_table_name;
end;
$$;

create trigger lead_touch_updated_at
before update on crm.lead
for each row execute function crm.touch_updated_at();

do $$
declare table_name text;
begin
    foreach table_name in array array[
        'lead_status_event', 'lead_activity', 'lead_assignment_event',
        'lead_external_reference', 'lead_audit'
    ] loop
        execute format('create trigger %I_reject_update before update on crm.%I for each row execute function crm.reject_append_only_mutation()', table_name, table_name);
        execute format('create trigger %I_reject_delete before delete on crm.%I for each row execute function crm.reject_append_only_mutation()', table_name, table_name);
        execute format('revoke update, delete on crm.%I from authenticated', table_name);
    end loop;
end $$;

do $$
declare table_name text;
begin
    foreach table_name in array array[
        'lead_source', 'lead', 'lead_status_event', 'lead_activity',
        'lead_assignment_event', 'lead_external_reference', 'lead_audit'
    ] loop
        execute format('alter table crm.%I enable row level security', table_name);
        execute format('alter table crm.%I force row level security', table_name);
        execute format('drop policy if exists crm_tenant_select on crm.%I', table_name);
        execute format('drop policy if exists crm_tenant_insert on crm.%I', table_name);
        execute format('drop policy if exists crm_tenant_update on crm.%I', table_name);
        execute format('create policy crm_tenant_select on crm.%I for select using (organization_id = current_setting(''app.organization_id'', true))', table_name);
        execute format('create policy crm_tenant_insert on crm.%I for insert with check (organization_id = current_setting(''app.organization_id'', true))', table_name);
        execute format('create policy crm_tenant_update on crm.%I for update using (organization_id = current_setting(''app.organization_id'', true)) with check (organization_id = current_setting(''app.organization_id'', true))', table_name);
    end loop;
end $$;

comment on schema crm is 'Tenant-aware common CRM (Leads) data; organization_id is the isolation boundary.';
