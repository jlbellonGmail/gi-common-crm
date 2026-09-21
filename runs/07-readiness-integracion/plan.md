# Plan: Feature 07-readiness-integracion

## Secuencia de implementación

### Paso 1 — Manifiesto de dependencias de test (`requirements-crm-dev.txt`)

Crear `requirements-crm-dev.txt` en la raíz, mismo formato que
`requirements-dev.txt`: comentario de propósito + paquetes fijados con
`==`. Incluye `pytest==8.3.5` (misma versión que el circuito, para no
introducir una segunda versión de pytest en el repo), `httpx==0.28.1`
(requerido por `starlette.testclient.TestClient`, no declarado como
dependencia transitiva de `fastapi`). No incluye `fastapi`/`pydantic`/
`psycopg` — esos ya se instalan vía los extras `[http,postgres]` de
`pyproject.toml` (ADR-C02, ya mergeado); duplicarlos en un requirements
aparte arriesgaría versiones divergentes entre los dos manifiestos.

### Paso 2 — Extender `scripts/validate-supply-chain.ps1`

Generalizar el `foreach` que hoy itera literalmente sobre
`@("requirements-dev.txt", "requirements-docs.txt")` para incluir también
`requirements-crm-dev.txt`, mismo criterio de "toda línea no-comentario
debe tener `==`". Cambio mínimo, sin tocar el resto del script (SHA-pin de
acciones, permisos de workflow, escaneo de secretos).

### Paso 3 — Reescribir el job `product-tests` de `.github/workflows/ci.yml`

Reemplazar por completo el step `Placeholder (sin stack definido)` y su
bloque de comentario `PLACEHOLDER` por:

1. Servicio `postgres:16-alpine` (declarado en `services:` del job, con
   `health-cmd`/`health-interval`/`health-retries`, puerto `5432:5432`).
2. `actions/setup-python@<mismo SHA ya usado en circuit-tests>` con
   `python-version: "3.12"`.
3. Un step de instalación: `pip install -e ".[http,postgres]"` seguido de
   `pip install -r requirements-crm-dev.txt`.
4. Un step de tests: `pytest -v tests_crm/` con
   `env: CRM_TEST_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/crm_test`.

El job conserva su nombre (`product-tests:`) y su ausencia de `if:` propio
(criterio ya cubierto por `tests/test_ci_workflow.py::
test_both_jobs_share_same_workflow_triggers`, que no se toca). Sin
`continue-on-error` en ningún step nuevo.

### Paso 4 — Reescribir el/los test(s) del circuito que asumían el placeholder

`tests/test_ci_workflow.py::test_product_tests_job_has_placeholder_marker`
asume literalmente que `PLACEHOLDER` sigue en el bloque de `product-tests`.
Se reemplaza por
`test_product_tests_job_runs_real_product_suite`, que verifica, sobre el
mismo `product_block` ya extraído por `_job_block`: ausencia de
`PLACEHOLDER`, presencia de `pytest -v tests_crm/`, presencia de
`postgres` (nombre del servicio) y de `CRM_TEST_DATABASE_URL`. El resto de
`tests/test_ci_workflow.py` no cambia.

**Corrección aplicada durante el build:** al correr `pytest -v tests/`
completo (no un subset) apareció un segundo test con la misma suposición,
en un archivo distinto: `tests/test_ci_integration.py::
test_product_tests_is_placeholder`. No estaba previsto en este paso
porque ninguno de los documentos de planificación había hecho un
inventario explícito de todos los tests que referencian `ci.yml`. Se
reescribió con el mismo criterio, como
`test_product_tests_runs_real_suite`, cuidando de no asumir ausencia
case-insensitive de la palabra "placeholder" en todo el archivo (el job
conserva un comentario en prosa que la menciona para explicar la
migración) — ver `spec.md` y `test-report-1.md` para el detalle completo.

### Paso 5 — Documentación

**Corrección aplicada durante el build:** el nombre de archivo real no es
libre por tema (`ci-real-product-tests.md`, como se redactó al planificar
este paso), sino el derivado de `Get-WorkUnitInfo -Mode Feature` para el
slug de esta unidad — `docs/tecnica/readiness-integracion.md` y
`docs/usuario/readiness-integracion.md` — mismo contrato real que ya usó
el Milestone previo (`scripts/workunit-lib.ps1`, consumido por
`scripts/update-doc-indexes.ps1`). Contenido: forma exacta del job,
diferencia explícita con `docs/tecnica/ci-wiring-product-tests.md`
heredado (ese describe por qué el placeholder era gate obligatorio pese a
estar vacío; éste describe qué lo reemplazó y por qué el "fuera de
alcance" de aquella feature no aplica a este repo derivado — ver spec.md,
"Supuestos y clarificaciones ya resueltas"). El par de usuario describe
cómo leer un fallo de `product-tests` en una PR real (log de pytest, no
artefactos de cobertura todavía) y cómo reproducir la misma suite en
local con Docker.

### Paso 6 — Evidencia de release readiness

Ejecutar `scripts/release-readiness.ps1` (read-only) contra el estado real
del repo tras el resto de los pasos, y volcar su salida real en
`runs/07-readiness-integracion/release-readiness.md` como evidencia. No se
crea tag ni release desde esta unidad.

### Paso 7 — Validaciones antes de PR

`pytest -v tests/` (circuito) y `pytest -v tests_crm/` (producto, local,
sin y con `CRM_TEST_DATABASE_URL` si Docker está disponible),
`pwsh ./scripts/sync-agentic-adapters.ps1 -Check`,
`pwsh ./scripts/validate-supply-chain.ps1`,
`pwsh ./scripts/check-integrity.ps1`. `ready-for-pr.ps1` sólo al final,
tras QA y code review internos.

## HITL

Al cerrar esta unidad: `ready-for-pr.ps1`, PR de `feature/07-readiness-
integracion` contra `develop`, esperar CI real (`gh pr checks`), y
detenerse en el HITL de merge — no se mergea sin autorización humana
explícita, igual criterio que el Milestone anterior.
