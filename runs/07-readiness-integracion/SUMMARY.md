# 07-readiness-integracion — CI real, supply-chain y evidencia de release

Estado: READY_FOR_PR (pendiente `ready-for-pr.ps1`, apertura de PR y CI
real en la PR)
Versión: legacy (sin `-Version` de work unit)
Tipo: Feature
SDD: FULL (ASSESS: `HIGH`)
PR: no creada todavía
Merge: no realizado

## Objetivo

Cerrar la brecha entre el Milestone `leads-core-implementation` (dominio
de Leads implementado y probado localmente, ya mergeado) y una PR
verificable con CI real: reemplazar el placeholder heredado del template
en el job `product-tests` por la suite real de `gi_crm` contra Postgres de
servicio, extender el supply-chain al nuevo manifiesto de dependencias de
test, documentar el resultado, y dejar evidencia real de
`release-readiness.ps1` para el futuro HITL de `v0.1.0`.

## Resultado

`product-tests` ya no es un placeholder: corre `pytest -v tests_crm/`
(66 tests) contra un servicio Postgres real dentro del job de CI, sin
`continue-on-error`. `requirements-crm-dev.txt` fija `pytest`/`httpx`;
`validate-supply-chain.ps1` lo valida igual que los otros dos
manifiestos. Documentación completa y enlazada. Suite del circuito en
verde (267 passed) tras corregir, con evidencia real, dos archivos de
test independientes que asumían el placeholder.

## Cambios principales

- `.github/workflows/ci.yml`: job `product-tests` reescrito (servicio
  `postgres:16-alpine`, instalación con extras `[http,postgres]` +
  `requirements-crm-dev.txt`, `pytest -v tests_crm/` con
  `CRM_TEST_DATABASE_URL`).
- `requirements-crm-dev.txt` (nuevo): `pytest==8.3.5`, `httpx==0.28.1`.
- `scripts/validate-supply-chain.ps1`: extendido para exigir también
  `requirements-crm-dev.txt` fijado con `==`.
- `tests/test_ci_workflow.py` y `tests/test_ci_integration.py`: ambos
  tenían una aserción independiente asumiendo el placeholder; ambas
  reescritas para verificar la forma real del job.
- `docs/tecnica/readiness-integracion.md` + `docs/usuario/readiness-
  integracion.md` (nuevos), enlazados en ambos índices vía
  `update-doc-indexes.ps1`.
- `runs/07-readiness-integracion/`: `spec.md`, `plan.md`, `tasks.md`,
  `decision.md`, `audit-1.md`, `test-report-1.md`, `code-review-1.md`,
  `release-readiness.md`.

## Validación

- `pytest -v tests/` (circuito): `267 passed, 2 warnings in 424.69s`. Una
  corrida previa mostró `1 failed, 266 passed` por un segundo test
  (`test_ci_integration.py::test_product_tests_is_placeholder`) no
  identificado en la spec inicial; corregido con el mismo criterio que el
  primero (ver `test-report-1.md`).
- `pytest -q tests_crm/` (producto, sin Postgres): `62 passed, 4 skipped`.
- `pytest -v tests_crm/test_dbapi_postgres.py` con Postgres real (Docker
  efímero, mismo procedimiento que corre el job de CI): `4 passed`.
- `sync-agentic-adapters.ps1 -Check`: sin diferencias.
- `validate-supply-chain.ps1`: OK (5 workflows, dependencias fijadas,
  incluido el nuevo manifiesto).
- `check-integrity.ps1`: PASS (warning esperado de `STATUS:AUTO`
  desactualizado en rama feature).
- `release-readiness.ps1 -Version v0.1.0`: rechazo esperado y documentado
  (script parametrizado para el ROADMAP/tag histórico de
  `template-starter`, no de este repositorio — ver hallazgo abajo).
- `code-review-1.md`: `approved`, sin hallazgos bloqueantes.

## Decisiones

- El alcance de `.github/workflows/ci.yml` y
  `scripts/validate-supply-chain.ps1` está autorizado explícitamente por
  `ROADMAP.md` de este repositorio para este ítem (ver `decision.md`); el
  "fuera de alcance" de `docs/tecnica/ci-wiring-product-tests.md` describe
  una decisión histórica del template, no una restricción vigente acá.
- No se toca el proyecto Supabase compartido: el Postgres del job de CI es
  un servicio efímero propio del run, igual criterio que la verificación
  manual con Docker local.
- No se decide ni publica ninguna release de `v0.1.0` desde esta unidad.

## Incidencias

- **`tests/test_ci_integration.py`** tenía una segunda aserción
  independiente sobre el placeholder, no anticipada en `spec.md` inicial;
  detectada al correr la suite completa (no un subset) y corregida con
  evidencia real — ver `test-report-1.md`.
- **`scripts/release-readiness.ps1`** heredado del template está
  parametrizado con ítems de `ROADMAP.md` y un tag histórico
  (`18-status-observabilidad`...`22-auditoria-release-v2`, `v1.1.0`)
  propios de `template-starter`, no de `gi-common-crm`. Rechaza
  correctamente al ejecutarlo, pero **no será utilizable tal cual como
  gate real del futuro `v0.1.0`** hasta que alguien decida y documente la
  propia lista de readiness de este proyecto. Queda registrado como
  pendiente de decisión humana (no bloqueante para esta unidad, cuyo
  alcance declarado era sólo ejecutar el script y documentar su salida
  real) — ver `release-readiness.md` y `STATUS.md`.
- Sin otras incidencias bloqueantes.

## Detalle

Con esta unidad, `product-tests` deja de ser un placeholder heredado y
pasa a verificar de verdad el paquete `gi_crm` en cada PR/push, con el
mismo nivel de exigencia que `circuit-tests`/`local-reconciler-tests`.
Lista para `ready-for-pr.ps1` una vez commiteado el diff vigente.
