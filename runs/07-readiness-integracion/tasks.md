# Tasks: Feature 07-readiness-integracion

## Dependencias y supply-chain

- [x] Crear `requirements-crm-dev.txt` con `pytest`/`httpx` fijados.
- [x] Extender `scripts/validate-supply-chain.ps1` para cubrir el nuevo
      manifiesto.

## CI real

- [x] Reescribir el job `product-tests` de `.github/workflows/ci.yml`:
      servicio Postgres, instalación con extras, `pytest -v tests_crm/`.
- [x] Reescribir `tests/test_ci_workflow.py::
      test_product_tests_job_has_placeholder_marker` →
      `test_product_tests_job_runs_real_product_suite`.
- [x] Corrección detectada durante el build: reescribir también
      `tests/test_ci_integration.py::test_product_tests_is_placeholder` →
      `test_product_tests_runs_real_suite` (segundo archivo independiente
      con la misma suposición, no identificado hasta correr `pytest -v
      tests/` completo — ver `spec.md`).

## Documentación

- [x] `docs/tecnica/readiness-integracion.md` (nombre real derivado de
      `Get-WorkUnitInfo -Mode Feature` para el slug `07-readiness-
      integracion`, no `ci-real-product-tests.md` como se redactó
      inicialmente en `plan.md`; corregido antes de enlazar en los
      índices).
- [x] `docs/usuario/readiness-integracion.md`.
- [x] Enlaces agregados a `docs/tecnica/index.md`/`docs/usuario/index.md`
      vía `scripts/update-doc-indexes.ps1` (mecanismo oficial, sin edición
      manual).

## Evidencia y cierre de unidad

- [x] `pytest -v tests/` (circuito) en verde: 267 passed (ver
      `test-report-1.md`).
- [x] `pytest -v tests_crm/` (producto, local, sin Postgres) en verde: 62
      passed, 4 skipped.
- [x] `pytest -v tests_crm/test_dbapi_postgres.py` con Postgres real
      (Docker efímero): 4 passed.
- [x] `pwsh ./scripts/sync-agentic-adapters.ps1 -Check` sin diferencias.
- [x] `pwsh ./scripts/validate-supply-chain.ps1` en verde.
- [x] `pwsh ./scripts/check-integrity.ps1` en verde (con warning esperado
      de STATUS:AUTO desactualizado respecto a `develop`, normal en una
      rama feature).
- [x] `scripts/release-readiness.ps1` ejecutado y su salida real
      documentada en `runs/07-readiness-integracion/release-readiness.md`
      (rechazo esperado: script heredado del template, parametrizado con
      ítems de `ROADMAP.md` y un tag histórico propios de
      `template-starter`, no de `gi-common-crm` — ver ese archivo).
- [x] `SUMMARY.md`, `audit-1.md`, `test-report-1.md`, `code-review-1.md`
      de esta unidad.
- [x] `ready-for-pr.ps1` corrido con éxito; PR #4 abierta contra `develop`
      (`https://github.com/jlbellonGmail/gi-common-crm/pull/4`).
- [x] CI real verde en la PR (`gh pr checks 4`), confirmado, no inferido:
      `circuit-tests` pass (3m30s), `local-reconciler-tests` pass (38s),
      `product-tests` pass (31s) — run `35671775612`.
- [ ] HITL de merge: detenerse, informar, esperar decisión humana.
