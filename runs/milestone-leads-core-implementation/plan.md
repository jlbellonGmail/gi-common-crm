# Plan: Milestone leads-core-implementation (ítems 02–06)

## Secuencia de implementación

Una sola rama/PR (`milestone/leads-core-implementation`), commits separados
por ítem para trazabilidad, en el orden de dependencia ya fijado por
`plan-crm.md`: 02 → 03 → (04 y 05 pueden solaparse; 05 depende de 03 y 04)
→ 06.

### Paso 1 — `gi_crm/models.py`, `gi_crm/errors.py` (base común)

Dataclasses `frozen, slots`: `RequestContext` (mismo contrato que
`gi_persons`: `user_id`, `organization_id`, `location_id`,
`correlation_id`, `trusted=True` obligatorio), `Lead`, `LeadSource`,
`LeadStatusEvent`, `LeadActivity`, `LeadAssignmentEvent`,
`LeadExternalReference`, `LeadAudit`, función `json_value()` para
serialización JSON-safe. Jerarquía `CrmError` con subclases
`ValidationError`, `NotFoundError`, `ForbiddenError`,
`VersionConflictError`, `InvalidTransitionError`,
`DuplicateExternalReferenceError`, `CoreUnavailableError`,
`PersonsUnavailableError`, `CapabilityUnavailableError`; cada una con
`code`, `safe_message`, `to_json()`.

### Paso 2 — `gi_crm/ports.py`, `gi_crm/authorization.py` (ítem 02)

`Protocol CoreApi` (sólo `authorize`, forma idéntica a
`gi_platform_core.CoreApi.authorize`), `Protocol PersonsApi`
(`find_duplicate_candidates`, `get_person`, `create_person`, forma
idéntica a `gi_persons.api.PersonsApi`), `Protocol AuditSink`, `Protocol
LeadStore` (create/get/list/update/append_status/append_activity/
append_assignment/add_external_reference/candidates). Helper
`require(context, core_api, permission, location_id=None)` que llama
`CoreApi.authorize` y traduce `allowed=False` o error de transporte en
`ForbiddenError`/`CoreUnavailableError` — nunca permite por defecto.
Fakes de test (`FakeCoreApi`, `FakePersonsApi`) en `tests_crm/fakes.py`.
Adaptadores `adapters/core_http.py`/`adapters/persons_http.py` contra el
contrato documentado en `docs/tecnica/contrato-core.md`/
`contrato-persons.md`, con docstring explícito de bloqueo end-to-end.

### Paso 3 — `gi_crm/service.py`, `gi_crm/memory.py` (ítem 03)

`LeadService`: `create_lead`, `get_lead`, `list_leads` (filtros status/
owner/source/person_id/rango de fechas + paginación), `update_lead`,
`change_status` (valida transición vía tabla de transiciones válidas
interna al service), `assign_lead`/`reassign_lead`, `add_activity`,
`list_activities`, `list_status_history`, `link_person` (usa
`PersonsApi.find_duplicate_candidates`/`get_person`), `add_external_
reference`, `convert_lead`, `close_lead` (motivo). Cada método llama
`require()` con el permiso `crm:lead:<acción>` correspondiente antes de
tocar `LeadStore`. `InMemoryLeadStore` implementa `LeadStore` con
diccionarios indexados por `(organization_id, id)`, aplica el mismo
filtrado por organización que hará el store real (para que las pruebas de
aislamiento sean significativas incluso en memoria). Tests unitarios de
dominio, transiciones, duplicados, concurrencia y aislamiento cruzado
corren aquí primero, contra `InMemoryLeadStore` + fakes.

### Paso 4 — `supabase/migrations/*_crm.sql`, `gi_crm/dbapi.py` (ítem 04)

Migración SQL cruda: esquema `crm`, tablas `lead`, `lead_source`,
`lead_status_event`, `lead_activity`, `lead_assignment_event`,
`lead_external_reference`, `lead_audit`; PK compuesta
`(organization_id, id)`; políticas RLS por
`current_setting('app.organization_id', true)` en cada tabla; triggers
`updated_at`; trigger/tabla de auditoría append-only (mismo patrón que
`persons.sql`, no se inventa uno nuevo). `PostgresLeadStore` implementa
`LeadStore` vía DB-API 2.0 puro (parámetros posicionales, sin ORM, sin
importar `psycopg` dentro del store — la fábrica de conexión se inyecta),
aplicando `SET LOCAL app.organization_id` por transacción antes de cada
operación. Pruebas reales: `tests_crm/test_dbapi_postgres.py`, activas sólo
si `CRM_TEST_DATABASE_URL` está definido (mismo patrón que Persons),
aplicando la migración sobre una base efímera antes de cada sesión de
tests.

### Paso 5 — `gi_crm/api.py`, `gi_crm/http/*` (ítem 05)

`LeadsApi`: fachada JSON-safe sobre `LeadService`, mismo `CursorCodec`
(HMAC-firmado) que usa `gi_persons` para paginación, `error()` para mapear
excepciones `CrmError` a payload JSON-safe sin fuga de detalles internos.
`http/app.py` (FastAPI, *extra* `[http]`), `http/schemas.py` (Pydantic),
`http/errors.py` (mapeo `CrmError` → status HTTP). Contexto de tenant por
cabeceras confiables (`X-GI-User-Id`, `X-GI-Organization-Id`,
`X-GI-Location-Id`). OpenAPI autogenerado por FastAPI, sin mantenimiento
manual. Tests de contrato ejecutan la misma batería de casos contra
`LeadsApi` directamente y contra `TestClient` del HTTP, comparando
equivalencia funcional.

### Paso 6 — Seguimiento multivertical (ítem 06)

Extiende `LeadService`/`LeadsApi` con los métodos de actividad/asignación/
conversión ya diseñados en el paso 3 si no quedaron completos ahí (algunos
pueden implementarse antes por conveniencia técnica; el ítem 06 es el punto
de aceptación funcional completo, no necesariamente el primer código
escrito). Pruebas específicas de `add_external_reference`/`convert_lead`
con la restricción `UNIQUE(organization_id, vertical_code, external_type,
external_id)` y de que `gi_crm` no importa ni referencia ninguna vertical
por nombre (test estático simple sobre los imports del paquete).

### Paso 7 — Pruebas reales de persistencia (sin tocar CI)

`tests_crm/test_dbapi_postgres.py` usa `pytest.importorskip("psycopg")` y
se salta (`pytest.skip`) si `CRM_TEST_DATABASE_URL` no está definida —
mismo patrón que `tests_persons/test_supabase_integration.py`. Se verifica
localmente contra un Postgres efímero (Docker) antes de declarar el paso
hecho, con evidencia del resultado real en `test-report-1.md`. El
placeholder `product-tests` de `.github/workflows/ci.yml` **no se toca en
este Milestone**: `ROADMAP.md` asigna explícitamente "CI real (product-tests
deja de ser placeholder)" a `07-readiness-integracion`, y
`gi-common-persons` siguió el mismo patrón en su propio milestone 02-07
(dejó el placeholder intacto hasta su propia unidad 07). Ver "Contradicción
resuelta" en `decision.md` sobre la frase de `plan-crm.md` que sugería lo
contrario.

### Paso 8 — Documentación

`docs/tecnica/modelo-datos-crm.md` (esquema real, RLS, triggers),
`docs/tecnica/contrato-core.md`/`contrato-persons.md` (contrato HTTP
documentado + estado bloqueado), `docs/tecnica/api-publica-crm.md`
(`LeadsApi` + HTTP + OpenAPI), `docs/tecnica/ciclo-vida-leads.md` (máquina
de estados), y sus equivalentes en `docs/usuario/`. Actualizar
`docs/tecnica/index.md`/`docs/usuario/index.md` vía
`update-doc-indexes.ps1` (Milestone sí soporta indexado, a diferencia de
Maintenance).

## Validaciones antes de PR

- `pytest -q tests/` (circuito) y `pytest -q tests_crm/` (producto,
  incluyendo el subconjunto real de Postgres si hay Docker disponible
  localmente) en verde, sin `continue-on-error`.
- `scripts/sync-agentic-adapters.ps1 -Check`.
- `scripts/validate-supply-chain.ps1` (si aplica a las dependencias nuevas
  introducidas por los extras `[http]`/`[postgres]`).
- Confirmación explícita, por test, de que `gi_crm` no importa
  `gi_platform_core` ni `gi_persons`.
- `ready-for-pr.ps1 -Mode Milestone -Slug leads-core-implementation` sólo
  con los 5 ítems en estado verificable.

## HITL

Único HITL de esta unidad: decisión humana MERGE/NO MERGE sobre la PR del
Milestone contra `develop`, con CI verde real (incluye el servicio Postgres
del paso 7). El agente no ejecuta el merge; a lo sumo prepara evidencia
para `complete-approved-pr.ps1 -GovernanceMode SingleMaintainer` si el
humano decide usar ese camino, o espera el merge directo humano en GitHub
(ambos caminos ya usados y válidos en esta misma unidad de trabajo según
`AGENTS.md`).
