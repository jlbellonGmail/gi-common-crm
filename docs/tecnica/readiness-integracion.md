# Readiness e integración: CI real de product-tests

Esta feature (`07-readiness-integracion`) cierra la brecha entre el
milestone `02-06-leads-core-implementation` (dominio, persistencia y API
de `gi_crm` ya mergeados) y un `v0.1.0` publicable: reemplaza el job
`product-tests` de `.github/workflows/ci.yml`, hasta ahora un placeholder
heredado del template (ver `docs/tecnica/ci-wiring-product-tests.md`), por
la suite real de `gi_crm` (`tests_crm/`) corriendo contra un Postgres real
de servicio, extiende `scripts/validate-supply-chain.ps1` al nuevo
manifiesto `requirements-crm-dev.txt`, y documenta la evidencia de
`scripts/release-readiness.ps1` usada para el HITL de release. Los jobs
`circuit-tests` y `local-reconciler-tests` no se tocan.

## Por qué corresponde a esta unidad, no al template

`docs/tecnica/ci-wiring-product-tests.md` documenta que "agregar build/test
real de cualquier stack de producto" quedaba fuera de alcance de la
feature que introdujo el placeholder (`04-ci-wiring-product-tests`, en el
template). Es correcto para ese repositorio: `template-starter` no tiene
stack propio. `gi-common-crm` sí lo tiene, ya decidido en
`docs/tecnica/arquitectura-crm.md` (ADR-C02: paquete `gi_crm`, Python
≥3.12, sin dependencias de runtime obligatorias, extras opcionales
`[http]`/`[postgres]`), y `ROADMAP.md` de este repositorio asigna
explícitamente esta tarea al ítem `07-readiness-integracion`. Ver
`runs/07-readiness-integracion/decision.md` para el detalle completo del
razonamiento de precedencia (`AGENTS.md`, orden de autoridad).

## Forma exacta del job

```yaml
product-tests:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16-alpine
      env:
        POSTGRES_PASSWORD: postgres
        POSTGRES_DB: crm_test
      ports:
        - 5432:5432
      options: >-
        --health-cmd "pg_isready -U postgres"
        --health-interval 5s
        --health-timeout 5s
        --health-retries 10
  steps:
    - uses: actions/checkout@...
    - name: Instalar Python 3.12
      uses: actions/setup-python@...
    - name: Instalar gi_crm con extras de test
      run: |
        pip install -e ".[http,postgres]"
        pip install -r requirements-crm-dev.txt
    - name: Tests de producto (pytest, Postgres de servicio)
      env:
        CRM_TEST_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/crm_test
      run: pytest -v tests_crm/
```

Puntos relevantes:

- El paquete se instala editable con los extras `[http,postgres]` — la
  misma fuente (`pyproject.toml`) que usaría un consumidor real de la
  biblioteca, no una lista duplicada de versiones. `fastapi`, `pydantic`
  y `psycopg` quedan fijados por rango ahí (ADR-C02); no se repiten en
  `requirements-crm-dev.txt` para no tener dos fuentes de verdad sobre la
  misma dependencia (ver `decision.md`).
- `requirements-crm-dev.txt` fija con `==` sólo lo que es exclusivo de la
  suite de tests y no forma parte de la biblioteca: `pytest` y `httpx`
  (este último requerido por `starlette.testclient.TestClient`, que usa
  `tests_crm/test_http_contract.py`, y que no es dependencia transitiva
  declarada de la versión de `fastapi` instalada).
- El Postgres de servicio es efímero, propio del run de CI — no es el
  proyecto Supabase compartido con `gi-platform-core`/`gi-common-persons`.
  Tocar ese proyecto compartido queda fuera de alcance de esta unidad (ver
  `ROADMAP.md`, ítem `08-persistencia-supabase-real`, diferido y sujeto a
  autorización humana explícita).
- `CRM_TEST_DATABASE_URL` es la misma variable de entorno que ya usan
  localmente los tests de `tests_crm/` contra un contenedor Docker
  (documentado en `runs/milestone-leads-core-implementation/
  test-report-1.md`); CI sólo automatiza el mismo procedimiento manual ya
  verificado.
- Sin `continue-on-error` ni equivalente: si la suite falla, el job queda
  rojo y bloquea el merge, mismo nivel de exigencia que `circuit-tests` y
  `local-reconciler-tests`.

## Supply-chain

`scripts/validate-supply-chain.ps1` valida `requirements-crm-dev.txt`
igual que ya validaba `requirements-dev.txt`/`requirements-docs.txt`
(toda línea no comentada debe estar fijada con `==`). Las acciones
(`actions/checkout`, `actions/setup-python`) usan la misma referencia
SHA-pinned ya vigente en `circuit-tests`/`local-reconciler-tests`, sin
introducir ninguna acción nueva.

## Verificación

`tests/test_ci_workflow.py::test_product_tests_job_runs_real_product_suite`
reemplaza a `test_product_tests_job_has_placeholder_marker`: verifica por
substring de texto plano (mismo patrón sin parsear YAML que el resto del
archivo) que el bloque de `product-tests` ya no contiene `PLACEHOLDER`, y
sí contiene `postgres`, `CRM_TEST_DATABASE_URL` y `pytest -v tests_crm/`.
El resto de aserciones del archivo (sobre `circuit-tests` y
`local-reconciler-tests`) no cambia.

## No confundir con `08-persistencia-supabase-real`

Este job prueba `gi_crm` contra un Postgres real, pero efímero y propio
de cada run de CI — no contra el proyecto Supabase compartido en uso por
`gi-platform-core` y `gi-common-persons`. Desplegar las migraciones de
`crm.*` a ese proyecto compartido es una acción de infraestructura
externa y difícil de revertir, y queda deliberadamente fuera de esta
unidad.
