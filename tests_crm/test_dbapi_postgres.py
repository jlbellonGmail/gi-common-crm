"""Persistencia real y aislamiento RLS contra Postgres efímero (spec.md #12).

Fuera de alcance de este Milestone: CI real (ver decision.md, sección
"Contradicción resuelta..."). Esta prueba corre sólo localmente/manualmente
contra un Postgres efímero (Docker) cuando CRM_TEST_DATABASE_URL está
definida; en su ausencia se salta, igual que
tests_persons/test_supabase_integration.py hace con PERSONS_TEST_DATABASE_URL.
"""
import os
from pathlib import Path
from uuid import uuid4

import pytest

psycopg = pytest.importorskip("psycopg")

from gi_crm.dbapi import PostgresLeadStore  # noqa: E402
from gi_crm.errors import DuplicateExternalReferenceError, VersionConflictError  # noqa: E402
from gi_crm.models import Lead, LeadExternalReference  # noqa: E402

DATABASE_URL = os.environ.get("CRM_TEST_DATABASE_URL")

pytestmark = pytest.mark.integration


def _apply_migration(conn):
    # `authenticated` es provisto por Supabase en el proyecto real; en un
    # Postgres efímero (sin Supabase) hay que crearlo aquí para poder
    # probar RLS bajo el mismo rol no-superusuario que usa la migración
    # (ver GRANT ... TO authenticated en el propio .sql). Esto es
    # infraestructura de la prueba local, no un cambio a la migración.
    with conn.cursor() as cur:
        cur.execute("do $$ begin if not exists (select from pg_roles where rolname = 'authenticated') then create role authenticated; end if; end $$;")
    sql = Path("supabase/migrations/20260921000100_crm.sql").read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


@pytest.fixture(scope="module")
def migrated_database():
    if not DATABASE_URL:
        pytest.skip("CRM_TEST_DATABASE_URL not set; skipping real-Postgres integration test")
    # Migración aplicada una sola vez por módulo (igual que un despliegue
    # real: una migración no se reaplica por prueba). Cada test opera
    # sobre su propia conexión/transacción y se revierte al terminar.
    setup_conn = psycopg.connect(DATABASE_URL)
    _apply_migration(setup_conn)
    setup_conn.close()
    yield DATABASE_URL


@pytest.fixture
def connection(migrated_database):
    conn = psycopg.connect(migrated_database)
    conn.autocommit = False
    # RLS no aplica al superusuario de conexión (ni siquiera con FORCE ROW
    # LEVEL SECURITY): las pruebas deben correr como el rol no-privilegiado
    # real, igual que tests_persons/test_supabase_integration.py.
    with conn.cursor() as cur:
        cur.execute("set role authenticated")
    yield conn
    conn.rollback()
    conn.close()


def _set_tenant(conn, organization_id, user_id):
    with conn.cursor() as cur:
        cur.execute("select set_config('app.organization_id', %s, false)", (organization_id,))
        cur.execute("select set_config('app.user_id', %s, false)", (user_id,))


def test_insert_and_read_back_lead_under_own_tenant(connection):
    store = PostgresLeadStore(lambda: connection)
    _set_tenant(connection, "org-a", "user-a")
    lead = Lead(uuid4(), "org-a", title="Lead real")
    store.insert_lead(connection, lead, "user-a")
    row = store.get_lead(connection, "org-a", lead.lead_id)
    assert row is not None
    assert row[2] == "new"


def test_rls_blocks_reading_other_org_lead(connection):
    store = PostgresLeadStore(lambda: connection)
    _set_tenant(connection, "org-a", "user-a")
    lead = Lead(uuid4(), "org-a", title="Lead de A")
    store.insert_lead(connection, lead, "user-a")

    _set_tenant(connection, "org-b", "user-b")
    row = store.get_lead(connection, "org-a", lead.lead_id)
    assert row is None


def test_update_lead_fields_conflicts_on_stale_version(connection):
    store = PostgresLeadStore(lambda: connection)
    _set_tenant(connection, "org-a", "user-a")
    lead = Lead(uuid4(), "org-a", title="Lead")
    store.insert_lead(connection, lead, "user-a")
    store.bump_lead_version(connection, "org-a", lead.lead_id, 1)
    with pytest.raises(VersionConflictError):
        store.bump_lead_version(connection, "org-a", lead.lead_id, 1)


def test_duplicate_external_reference_is_rejected(connection):
    store = PostgresLeadStore(lambda: connection)
    _set_tenant(connection, "org-a", "user-a")
    lead = Lead(uuid4(), "org-a", title="Lead")
    store.insert_lead(connection, lead, "user-a")
    reference = LeadExternalReference(uuid4(), "org-a", lead.lead_id, "dental", "patient", "123")
    store.insert_external_reference(connection, reference)
    dup = LeadExternalReference(uuid4(), "org-a", lead.lead_id, "dental", "patient", "123")
    with pytest.raises(DuplicateExternalReferenceError):
        store.insert_external_reference(connection, dup)
