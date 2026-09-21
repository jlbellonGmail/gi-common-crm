# milestone-leads-core-implementation — dominio Leads completo (ítems 02–06)

Estado: EN_REVISIÓN
Versión: legacy (sin `-Version` de work unit; ver `work-unit.json`)
Tipo: Milestone
SDD: FULL (ASSESS: `HIGH`)
PR: no creada
Merge: no realizado

## Objetivo

Implementar la primera versión funcional (v0.1.0) del dominio de Leads de
GI-COMMON-CRM: contratos de integración con Core/Persons, dominio con
máquina de estados y detección de duplicados, persistencia aislada por
organización sobre PostgreSQL, API pública de biblioteca y HTTP, y
seguimiento multivertical — probado real, documentado e integrable por las
verticales del Sistema Integral GI, sin acoplar CRM a ninguna vertical
concreta.

## Resultado

Los 5 ítems del manifest (`02-contratos-integracion`, `03-dominio-leads`,
`04-persistencia-aislamiento`, `05-api-publica`,
`06-seguimiento-multivertical`) están implementados, probados y
documentados. `gi_crm` es un paquete completo sin dependencias de runtime
obligatorias (FastAPI/psycopg como extras opcionales), con 62 tests en
verde sin dependencias externas y 4 tests de persistencia real verificados
contra Postgres efímero (Docker).

## Cambios principales

- `gi_crm/`: `models.py`, `errors.py`, `ports.py` (`Protocol CoreApi`/
  `PersonsApi` locales, sin importar `gi_platform_core`/`gi_persons`),
  `authorization.py` (`require()` fail-safe), `service.py` (`LeadService`
  con máquina de estados, concurrencia optimista, detección de duplicados
  vía Persons), `memory.py` (`InMemoryLeadStore`), `dbapi.py`
  (`PostgresLeadStore` DB-API 2.0 puro), `api.py` (`LeadsApi`, paginación
  por cursor firmado), `adapters/core_http.py`/`adapters/persons_http.py`
  (bloqueados/documentados, no verificables end-to-end), `http/` (FastAPI
  opcional).
- `supabase/migrations/20260921000100_crm.sql`: esquema `crm.*`, PK
  compuesta `(organization_id, id)`, RLS forzado, triggers de auditoría
  append-only.
- `tests_crm/`: 16 archivos, cobertura de los 12 criterios de aceptación
  de `spec.md` (límites de módulos, aislamiento multitenant, autorización
  fail-safe, Persons caído, cardinalidad, máquina de estados, concurrencia
  optimista, referencias externas/conversión, persistencia real,
  equivalencia biblioteca/HTTP, bloqueo de adaptadores HTTP, suite
  completa sin dependencias externas).
- `docs/tecnica/`+`docs/usuario/`: un documento por ítem del manifest
  (`contratos-integracion`, `dominio-leads`, `persistencia-aislamiento`,
  `api-publica`, `seguimiento-multivertical`), registrados en los índices
  vía `update-doc-indexes.ps1`.
- Corrección transparente en `spec.md`/`plan.md`/`tasks.md`: los nombres
  de documentación reales se derivan de `Get-WorkUnitInfo -Mode Feature`
  por ítem (contrato real de `workunit-lib.ps1`), no de la lista libre por
  tema redactada antes de leer el script.

## Validación

- `pytest -q tests/`: `267 passed, 2 warnings in 351.53s` (sin
  regresiones; el diff de esta unidad no toca `scripts/` ni `tests/`). Ver
  `test-report-1.md` para el detalle de una corrida previa con 3 fallos
  aislados no reproducibles (contención local, no regresión).
- `pytest -q tests_crm/`: `62 passed, 4 skipped, 2 warnings in 6.57s`
  (skips = subset de Postgres real sin `CRM_TEST_DATABASE_URL`).
- `pytest -q tests_crm/test_dbapi_postgres.py` con
  `CRM_TEST_DATABASE_URL` apuntando a `postgres:16-alpine` efímero vía
  Docker: `4 passed`. En el proceso se encontró y corrigió un bug real de
  producto (`PostgresLeadStore.bump_lead_version` enviaba `"version + 1"`
  como valor parametrizado en vez de expresión SQL literal) — evidencia
  completa en `test-report-1.md`.
- `sync-agentic-adapters.ps1 -Check`: adaptadores sincronizados.
- `validate-supply-chain.ps1`: OK (5 workflows, acciones SHA-pinned,
  permisos explícitos, dependencias fijadas).
- `code-review-1.md`: `approved`, sin hallazgos bloqueantes, verificación
  cruzada de los 12 criterios de aceptación contra el test correspondiente.

## Decisiones

- Alcance de esta unidad no incluye reemplazar el placeholder
  `product-tests` de `.github/workflows/ci.yml` (pertenece a
  `07-readiness-integracion`, ver `decision.md` — "Contradicción
  resuelta").
- No se toca el proyecto Supabase compartido de Core/Persons; toda prueba
  de persistencia real corre contra un contenedor Postgres efímero local
  (`08-persistencia-supabase-real` sigue diferida y requiere autorización
  humana previa, según `ROADMAP.md`).

## Incidencias

- Ninguna bloqueante. Riesgo ya registrado en `spec.md`: Persons sin
  release propio todavía (fundación movediza), y adaptadores HTTP de
  Core/Persons no verificables end-to-end hasta que esos repos publiquen
  un servicio real — ambos aceptados y documentados, no ocultos.

## Detalle

La unidad implementa producto funcional real (no esqueleto): dominio,
persistencia con RLS forzado verificado contra Postgres real, dos
modalidades de API equivalentes, y seguimiento multivertical sin acoplar
`gi_crm` a ninguna vertical concreta. Lista para `ready-for-pr.ps1` una vez
confirmada esta evidencia.
