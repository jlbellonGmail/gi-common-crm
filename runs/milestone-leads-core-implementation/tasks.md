# Tasks: Milestone leads-core-implementation (ítems 02–06)

Checklist operativo derivado de `plan.md`. Cada casilla se marca sólo tras
verificación real (test pasando, archivo escrito y revisado), no por
haberla redactado.

## 02-contratos-integracion

- [ ] `gi_crm/models.py`: `RequestContext` y entidades base (`frozen,
      slots`), `json_value()`.
- [ ] `gi_crm/errors.py`: jerarquía `CrmError` completa.
- [ ] `gi_crm/ports.py`: `Protocol CoreApi`, `Protocol PersonsApi`,
      `Protocol AuditSink`, `Protocol LeadStore`.
- [ ] `gi_crm/authorization.py`: `require()` fail-safe.
- [ ] `gi_crm/adapters/core_http.py`, `gi_crm/adapters/persons_http.py`
      con docstring de bloqueo end-to-end explícito.
- [ ] `tests_crm/fakes.py`: `FakeCoreApi`, `FakePersonsApi`.
- [ ] `tests_crm/test_ports_contract.py`: verifica que los `Protocol`
      calzan estructuralmente con firmas reales documentadas de
      `gi_platform_core`/`gi_persons` (sin importarlos como dependencia).
- [ ] Test estático: `gi_crm` no importa `gi_platform_core` ni `gi_persons`
      en ningún módulo.
- [ ] Permisos `crm:lead:*` documentados en
      `docs/tecnica/contrato-core.md`.

## 03-dominio-leads

- [ ] `gi_crm/service.py`: `LeadService` completo (create/get/list/update/
      change_status/assign/reassign/add_activity/list_activities/
      list_status_history/link_person/add_external_reference/
      convert_lead/close_lead).
- [ ] Tabla de transiciones válidas y validación de `InvalidTransitionError`.
- [ ] `gi_crm/memory.py`: `InMemoryLeadStore` con filtrado por
      organización.
- [ ] `tests_crm/test_service_domain.py`: casos de máquina de estados
      (válidas/ inválidas), `archived` desde no terminal.
- [ ] `tests_crm/test_service_duplicates.py`: detección de duplicados vía
      `PersonsApi.find_duplicate_candidates`, `PersonsUnavailableError`
      si Persons falla.
- [ ] `tests_crm/test_service_concurrency.py`: `VersionConflictError` con
      `version` desactualizada.
- [ ] `tests_crm/test_tenant_isolation.py`: organización A no ve/afecta
      Leads/actividades/historial/duplicados de organización B.
- [ ] `tests_crm/test_authorization.py`: sin permiso deniega,
      `CoreUnavailableError` si Core falla, respeto de `location_id`.
- [ ] `tests_crm/test_cardinality.py`: misma Person con N Leads sin
      colisión, sin `UNIQUE` implícito.

## 04-persistencia-aislamiento

- [ ] `supabase/migrations/<timestamp>_crm.sql`: esquema `crm`, tablas,
      PKs compuestas, RLS, triggers `updated_at`, auditoría append-only.
- [ ] `gi_crm/dbapi.py`: `PostgresLeadStore` DB-API 2.0 puro.
- [ ] `tests_crm/test_dbapi_postgres.py`: activo con
      `CRM_TEST_DATABASE_URL`; aplica migración, prueba RLS real (dos
      `organization_id` distintos, sin bypass), idempotencia de la
      migración.
- [ ] Verificación manual/local con Docker Postgres antes de confiar sólo
      en CI.

## 05-api-publica

- [ ] `gi_crm/api.py`: `LeadsApi`, `CursorCodec`, `error()`.
- [ ] `gi_crm/http/app.py`, `schemas.py`, `errors.py` (extra `[http]`).
- [ ] `tests_crm/test_api_library.py`, `tests_crm/test_http_contract.py`:
      misma batería de casos, comparando equivalencia funcional.
- [ ] OpenAPI generado verificado (`/openapi.json` accesible en
      `TestClient`).
- [ ] Paginación por cursor: estabilidad entre páginas probada.

## 06-seguimiento-multivertical

- [ ] Completar/probar actividad, asignación/reasignación con historial en
      `LeadService`/`LeadsApi` si algo quedó pendiente del paso 03.
- [ ] `tests_crm/test_external_reference.py`: `UNIQUE(organization_id,
      vertical_code, external_type, external_id)` respetada, segundo
      intento rechazado explícitamente.
- [ ] `tests_crm/test_no_vertical_coupling.py`: ninguna vertical
      referenciada por nombre en `gi_crm`.

## Persistencia real y documentación

- [ ] `tests_crm/test_dbapi_postgres.py` en verde localmente con
      `CRM_TEST_DATABASE_URL` (Docker Postgres efímero); se salta sin esa
      variable, igual que `test_supabase_integration.py` de Persons. No se
      toca `.github/workflows/ci.yml` en este Milestone (alcance de
      `07-readiness-integracion` según `ROADMAP.md`).
- [ ] `docs/tecnica/modelo-datos-crm.md`, `contrato-core.md`,
      `contrato-persons.md`, `api-publica-crm.md`, `ciclo-vida-leads.md`.
- [ ] Equivalentes en `docs/usuario/`.
- [ ] `docs/tecnica/index.md`/`docs/usuario/index.md` actualizados vía
      `update-doc-indexes.ps1 -Mode Milestone`.

## Cierre de unidad

- [ ] `pytest -q tests/` y `pytest -q tests_crm/` en verde, evidencia en
      `runs/milestone-leads-core-implementation/test-report-1.md`.
- [ ] `sync-agentic-adapters.ps1 -Check` en verde.
- [ ] `code-review-1.md` con veredicto `approved`.
- [ ] `ready-for-pr.ps1 -Mode Milestone -Slug leads-core-implementation`.
- [ ] PR contra `develop`, CI verde real confirmado (`gh pr checks`).
- [ ] HITL humano MERGE/NO MERGE.
- [ ] Tras merge: los 5 ítems en `[x]` en `ROADMAP.md`, `STATUS.md`
      sincronizado.
