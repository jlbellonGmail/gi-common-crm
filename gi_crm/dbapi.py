"""Optional DB-API 2.0 adapter; the caller owns the connection and role.

Mismo criterio que gi_persons.dbapi.PostgresPersonStore: no importa
psycopg ni ningun SDK de Supabase. El host suministra una fabrica de
conexion DB-API 2.0. RLS (crm.lead*, ver
supabase/migrations/20260921000100_crm.sql) es la defensa real; los
parametros de aplicacion se fijan por transaccion (SET LOCAL) y nunca se
interpolan en SQL. Igual que en Persons, esta es una implementacion de
referencia con el CRUD suficiente para probar aislamiento real vía
tests_crm/test_dbapi_postgres.py -- no una composicion automatica con
LeadService.transaction() de cero argumentos (eso lo arma el host real
al desplegar, igual que Persons).
"""
from contextlib import contextmanager

from .errors import DuplicateExternalReferenceError, VersionConflictError


class PostgresLeadStore:
    def __init__(self, connection_factory):
        self.connection_factory = connection_factory

    @contextmanager
    def transaction(self, organization_id: str, user_id: str):
        connection = self.connection_factory()
        try:
            with connection:
                with connection.cursor() as cur:
                    cur.execute("select set_config('app.organization_id', %s, true)", (organization_id,))
                    cur.execute("select set_config('app.user_id', %s, true)", (user_id,))
                yield connection
        finally:
            connection.close()

    def insert_lead(self, connection, lead, actor):
        with connection.cursor() as cur:
            cur.execute(
                """insert into crm.lead
                  (lead_id, organization_id, status, person_id, source_id, owner_user_id, title, description)
                  values (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    str(lead.lead_id), lead.organization_id, lead.status,
                    str(lead.person_id) if lead.person_id else None,
                    str(lead.source_id) if lead.source_id else None,
                    lead.owner_user_id, lead.title, lead.description,
                ),
            )

    def get_lead(self, connection, organization_id, lead_id):
        with connection.cursor() as cur:
            cur.execute(
                """select lead_id, organization_id, status, person_id, source_id, owner_user_id,
                          title, description, close_reason, version, created_at, updated_at
                   from crm.lead where organization_id = %s and lead_id = %s""",
                (organization_id, str(lead_id)),
            )
            return cur.fetchone()

    def update_lead_fields(self, connection, organization_id, lead_id, expected_version, **fields):
        assigns = ", ".join(f"{key} = %s" for key in fields)
        with connection.cursor() as cur:
            cur.execute(
                f"""update crm.lead set {assigns}
                   where organization_id = %s and lead_id = %s and version = %s
                   returning version""",
                (*fields.values(), organization_id, str(lead_id), expected_version),
            )
            row = cur.fetchone()
            if row is None:
                raise VersionConflictError()
            return row[0]

    def bump_lead_version(self, connection, organization_id, lead_id, expected_version):
        # `version + 1` es SQL literal, no un valor parametrizable: pasarlo
        # por update_lead_fields() lo insertaría como texto (ver bug real
        # detectado en tests_crm/test_dbapi_postgres.py). Se arma la
        # sentencia aparte, siempre con placeholders para los valores.
        with connection.cursor() as cur:
            cur.execute(
                """update crm.lead set version = version + 1
                   where organization_id = %s and lead_id = %s and version = %s
                   returning version""",
                (organization_id, str(lead_id), expected_version),
            )
            row = cur.fetchone()
            if row is None:
                raise VersionConflictError()
            return row[0]

    def insert_status_event(self, connection, event):
        with connection.cursor() as cur:
            cur.execute(
                """insert into crm.lead_status_event
                  (event_id, organization_id, lead_id, from_status, to_status, actor_user_id, reason)
                  values (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    str(event.event_id), event.organization_id, str(event.lead_id),
                    event.from_status, event.to_status, event.actor_user_id, event.reason,
                ),
            )

    def insert_activity(self, connection, activity):
        with connection.cursor() as cur:
            cur.execute(
                """insert into crm.lead_activity
                  (activity_id, organization_id, lead_id, actor_user_id, kind, notes)
                  values (%s, %s, %s, %s, %s, %s)""",
                (
                    str(activity.activity_id), activity.organization_id, str(activity.lead_id),
                    activity.actor_user_id, activity.kind, activity.notes,
                ),
            )

    def insert_assignment(self, connection, event):
        with connection.cursor() as cur:
            cur.execute(
                """insert into crm.lead_assignment_event
                  (assignment_id, organization_id, lead_id, from_user_id, to_user_id, actor_user_id)
                  values (%s, %s, %s, %s, %s, %s)""",
                (
                    str(event.assignment_id), event.organization_id, str(event.lead_id),
                    event.from_user_id, event.to_user_id, event.actor_user_id,
                ),
            )

    def insert_external_reference(self, connection, reference):
        with connection.cursor() as cur:
            try:
                cur.execute(
                    """insert into crm.lead_external_reference
                      (reference_id, organization_id, lead_id, vertical_code, external_type, external_id)
                      values (%s, %s, %s, %s, %s, %s)""",
                    (
                        str(reference.reference_id), reference.organization_id, str(reference.lead_id),
                        reference.vertical_code, reference.external_type, reference.external_id,
                    ),
                )
            except Exception as exc:
                # El host debe mapear la clase de violacion unique de su
                # driver a esta excepcion publica (igual criterio que
                # gi_persons.dbapi.PostgresPersonStore.insert_identifier).
                if "unique" in str(exc).lower():
                    raise DuplicateExternalReferenceError() from exc
                raise
