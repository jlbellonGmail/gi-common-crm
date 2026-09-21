# Ítem 04 — Persistencia y aislamiento (`crm.*`, RLS, PostgresLeadStore)

Ver [Arquitectura de CRM](arquitectura-crm.md) (ADR-C04) para la decisión
de no usar ORM. Este documento describe el esquema real y el adaptador.

## Esquema `crm.*`

`supabase/migrations/20260921000100_crm.sql` crea el esquema `crm` y las
tablas `lead_source`, `lead`, `lead_status_event`, `lead_activity`,
`lead_assignment_event`, `lead_external_reference`, `lead_audit`. Todas
usan PK compuesta `(organization_id, id)`. `lead_external_reference`
declara `UNIQUE(organization_id, vertical_code, external_type,
external_id)` — la referencia lógica hacia la entidad de vertical creada
al convertir el Lead (ADR-C01), nunca una FK física entre bases de datos.

Las tablas de historial (`lead_status_event`, `lead_activity`,
`lead_assignment_event`, `lead_external_reference`, `lead_audit`) son
append-only: un trigger `reject_append_only_mutation()` rechaza
`UPDATE`/`DELETE`, y se revoca el privilegio correspondiente al rol
`authenticated`. `lead.updated_at` se actualiza por trigger
(`touch_updated_at()`). Ambas funciones fijan `search_path = ''` desde el
origen (a diferencia de `gi-common-persons`, que lo incorporó en una
migración de hardening posterior — aquí se evita ese paso adicional por
tratarse de un esquema nuevo).

## Row-Level Security

Las 7 tablas tienen RLS **forzado** (`force row level security`, no sólo
`enable`), con política `crm_tenant_select/insert/update` condicionada a
`organization_id = current_setting('app.organization_id', true)`. Esto
aplica incluso al propietario de la tabla; sólo un rol `BYPASSRLS` (nunca
usado por la aplicación) lo evita.

## `PostgresLeadStore` (`gi_crm/dbapi.py`)

Adaptador DB-API 2.0 puro: no importa `psycopg` ni ningún SDK de Supabase,
el host inyecta la fábrica de conexión. Es una implementación de
**referencia**, no un `LeadStore` completo ni zero-arg-compatible con
`LeadService._transaction()` (mismo criterio real que
`gi_persons.PostgresPersonStore`): expone el CRUD mínimo para probar
aislamiento real, más `transaction(organization_id, user_id)` que fija
`app.organization_id`/`app.user_id` por transacción vía `SET LOCAL`
(nunca interpolados en SQL). `insert_external_reference` mapea cualquier
violación de índice único del driver a `DuplicateExternalReferenceError`,
igual criterio agnóstico de driver que `gi_persons.dbapi`.

## Pruebas reales contra Postgres efímero

`tests_crm/test_dbapi_postgres.py` se salta si `CRM_TEST_DATABASE_URL` no
está definida (igual patrón que
`tests_persons/test_supabase_integration.py` con
`PERSONS_TEST_DATABASE_URL`). Verificado localmente contra un contenedor
`postgres:16-alpine` efímero (Docker): aplica la migración una vez por
módulo, crea el rol `authenticated` (provisto por Supabase en el proyecto
real, ausente en un Postgres vanilla) y ejecuta las pruebas bajo `SET ROLE
authenticated` — el superusuario de conexión nunca activa RLS, ni con
`FORCE ROW LEVEL SECURITY`. Las 4 pruebas (inserción/lectura propia,
bloqueo de lectura cruzada entre organizaciones, conflicto de versión real,
rechazo de referencia externa duplicada) pasan contra Postgres real; este
ejercicio detectó y corrigió un bug real en
`PostgresLeadStore.bump_lead_version` (pasaba el literal SQL `"version +
1"` como valor parametrizado en vez de como expresión).

Fuera de alcance de este Milestone (ver
[decision.md](../../runs/milestone-leads-core-implementation/decision.md)):
CI real con Postgres de servicio pertenece a `07-readiness-integracion`
según `ROADMAP.md`, y el despliegue contra el proyecto Supabase compartido
pertenece a `08-persistencia-supabase-real`, condicionado a autorización
humana previa.
