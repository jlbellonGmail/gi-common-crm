```yaml
status: approved
attempt: 1
feedback:
  - Sin hallazgos bloqueantes. Suite del circuito y del producto en verde;
    corrección real detectada y aplicada durante el build (segundo test
    del circuito con la misma suposición de placeholder, no previsto en
    spec.md inicial).
```

# Test report 1 — 07-readiness-integracion

## `pytest -v tests/` (circuito)

Primera corrida completa, tras aplicar el cambio a `.github/workflows/
ci.yml` y reescribir sólo `tests/test_ci_workflow.py`:

```
FAILED tests/test_ci_integration.py::test_product_tests_is_placeholder[ci.yml]
1 failed, 266 passed, 2 warnings in 429.41s (0:07:09)
```

Hallazgo real: `tests/test_ci_integration.py` es un segundo archivo,
independiente de `tests/test_ci_workflow.py`, con su propia aserción
(`test_product_tests_is_placeholder`) que también asumía literalmente el
marcador `PLACEHOLDER` en `product-tests`. No estaba identificado en
`spec.md`/`plan.md` porque ninguno de los dos documentos había hecho un
inventario explícito de *todos* los tests que referencian `ci.yml` —
sólo se detectó al correr la suite completa del circuito, no un subset.

Corregido reescribiendo `test_product_tests_is_placeholder` →
`test_product_tests_runs_real_suite` con el mismo criterio que
`test_ci_workflow.py`: verifica ausencia del marcador `PLACEHOLDER` y del
step `Placeholder (sin stack definido)`, presencia de `postgres` y
`pytest -v tests_crm/`. No se asume ausencia case-insensitive de la
palabra "placeholder" en todo el archivo, porque el job conserva un
comentario en prosa que la menciona para explicar la migración (ver
`docs/tecnica/readiness-integracion.md`) — una aserción case-insensitive
habría producido un falso positivo contra ese comentario legítimo.

Corrida final, con ambos archivos de test corregidos:

```
267 passed, 2 warnings in 424.69s (0:07:04)
```

En verde, sin regresiones. Las dos advertencias son
`PytestUnhandledThreadExceptionWarning` por `UnicodeDecodeError` en hilos
lectores de subprocess (encoding `cp1252` de la consola de Windows),
preexistentes al circuito y no relacionadas con este diff.

## `pytest -q tests_crm/` (producto, sin Postgres real)

```
62 passed, 4 skipped, 3 warnings in 2.33s
```

Mismo resultado que el precedente documentado en
`runs/milestone-leads-core-implementation/test-report-1.md`: los 4 tests
salteados son `tests_crm/test_dbapi_postgres.py`, activados sólo con
`CRM_TEST_DATABASE_URL`. Este diff no modifica `gi_crm/` ni `tests_crm/`,
así que el resultado es el mismo que el ya verificado en el Milestone —
se reconfirma acá porque es la suite que el nuevo job `product-tests`
corre en CI.

## `pytest -v tests_crm/test_dbapi_postgres.py` con Postgres real (Docker)

```bash
docker run -d --rm --name crm-readiness-pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=crm_test -p 55432:5432 postgres:16-alpine
CRM_TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:55432/crm_test" \
  pytest -q tests_crm/test_dbapi_postgres.py
docker rm -f crm-readiness-pg
```

Resultado: **4 passed, 1 warning in 3.77s**
(`test_insert_and_read_back_lead_under_own_tenant`,
`test_rls_blocks_reading_other_org_lead`,
`test_update_lead_fields_conflicts_on_stale_version`,
`test_duplicate_external_reference_is_rejected`). Mismo procedimiento que
el job `product-tests` de `.github/workflows/ci.yml` ejecuta en CI (imagen
`postgres:16-alpine`, health-check, `CRM_TEST_DATABASE_URL` apuntando al
servicio): esta corrida local confirma que la forma del job funciona
antes de depender del run real de GitHub Actions en la PR.

## Otras validaciones

- `pwsh ./scripts/validate-supply-chain.ps1`: `Supply chain OK: 5
  workflows, acciones SHA-pinned, permisos explícitos y dependencias
  fijadas.` (cubre el nuevo `requirements-crm-dev.txt`).
- `pwsh ./scripts/sync-agentic-adapters.ps1 -Check`: `Adaptadores
  agenticos sincronizados.` (sin diferencias; esta unidad no toca
  `.agentic/`).
- `pwsh ./scripts/check-integrity.ps1`: `PASS integridad global
  ROADMAP/runs/SUMMARY/Git/STATUS`, con warning esperado de
  `STATUS:AUTO` desactualizado respecto al snapshot de `develop`
  (normal en cualquier rama feature activa; se regenera antes de
  `ready-for-pr.ps1`).
- `pwsh ./scripts/release-readiness.ps1 -Version v0.1.0`: rechazo
  esperado y documentado en `release-readiness.md` (script heredado
  parametrizado con ítems de `ROADMAP.md` propios de `template-starter`,
  no de este repositorio — hallazgo, no un fallo de esta unidad).

## Conclusión

Los 9 criterios de aceptación de `spec.md` tienen evidencia real
correspondiente: (1)-(2) confirmados por la ejecución local con Postgres
real y por `pytest -v tests_crm/`; (3)-(4) confirmados por `pytest -v
tests/` en verde (267 passed); (5)-(6) confirmados por las corridas de
`validate-supply-chain.ps1`/`sync-agentic-adapters.ps1 -Check`; (7)
pendiente hasta abrir la PR y confirmar `gh pr checks` (no inferible
localmente); (8) confirmado (`docs/tecnica/readiness-integracion.md` +
par de usuario, enlazados vía `update-doc-indexes.ps1`); (9) confirmado
(`release-readiness.md`). Veredicto: `approved`, intento 1.
