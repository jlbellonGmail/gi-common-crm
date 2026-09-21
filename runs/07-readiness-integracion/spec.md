# Spec: Feature 07-readiness-integracion

## Objetivo

Reemplazar el placeholder heredado del template en el job `product-tests`
de `.github/workflows/ci.yml` por ejecución real de `tests_crm/` contra
Postgres de servicio, completar la documentación de integración y
supply-chain correspondiente, y dejar evidencia verificable para el
próximo HITL (PR de esta unidad). No introduce funcionalidad de dominio
nueva: es la unidad de "readiness" que cierra la brecha entre "implementado
y probado localmente" (Milestone `leads-core-implementation`) y "probado
en CI en cada PR".

## Contexto

El Milestone `leads-core-implementation` (ítems 02-06) está mergeado a
`develop` (PR #3, merge commit `93b8d68`) y cerrado en `ROADMAP.md`. Su
propio `decision.md` registró explícitamente que la responsabilidad de
sustituir el placeholder de `product-tests` pertenece a esta unidad, no al
Milestone, por precedencia de `ROADMAP.md` sobre `plan-crm.md` (ver
`runs/milestone-leads-core-implementation/decision.md`, sección
"Contradicción resuelta").

`gi_crm` ya tiene su decisión de stack fijada y mergeada
(`docs/tecnica/arquitectura-crm.md`, ADR-C02): paquete Python ≥3.12, cero
dependencias de runtime obligatorias, extras opcionales `[http]`
(`fastapi`, `pydantic`) y `[postgres]` (`psycopg[binary]`). No hace falta
una decisión de arquitectura nueva para esta unidad: sólo instalar esos
extras ya declarados y ejecutar la suite ya escrita
(`tests_crm/`, 66 tests: 62 corren sin dependencias externas, 4 requieren
`CRM_TEST_DATABASE_URL`).

`docs/tecnica/ci-wiring-product-tests.md` (heredado del template,
feature `04-ci-wiring-product-tests`) documenta por qué `product-tests` es
gate obligatorio desde que se creó, aunque estuviera vacío, y dice
explícitamente que "agregar build/test real de cualquier stack de
producto" queda fuera de alcance de **esa** feature — porque el template
en sí no tiene stack propio. Ese documento describe una decisión histórica
del template, no una restricción vigente para este repositorio derivado,
que ya declaró su propio stack. Se registra esta lectura como
clarificación no bloqueante en la sección correspondiente más abajo, no
como contradicción abierta.

Hallazgo registrado en `STATUS.md` (no accionable desde aquí): el
`decision.md` del Milestone citó a `gi-common-persons` como precedente de
haber reemplazado su propio placeholder en su unidad `07-readiness-
integracion`; reverificado contra el `develop` real de `gi-common-persons`
(commit `433b651`), el placeholder sigue literal ahí pese a que su
`ROADMAP.md` marca esa unidad como `[x]`. No se modifica `gi-common-
persons`; esta unidad no tiene un ejemplo real que copiar de un repo
hermano y diseña el job desde cero, a partir de los comandos ya verificados
manualmente en `runs/milestone-leads-core-implementation/test-report-1.md`.

## Alcance

1. **CI real (`product-tests`)**: en `.github/workflows/ci.yml`, reemplazar
   por completo el step `Placeholder (sin stack definido)` del job
   `product-tests` por: checkout (ya existe), instalación de Python 3.12,
   un servicio Postgres efímero (contenedor de servicio de GitHub Actions,
   no el Supabase compartido), instalación de `gi_crm` con extras
   `[http,postgres]` más las dependencias de test fijadas, y
   `pytest -v tests_crm/` con `CRM_TEST_DATABASE_URL` apuntando al servicio.
   Sin `continue-on-error`: si la suite falla, el job queda rojo.
2. **Dependencias de test fijadas**: nuevo manifiesto
   `requirements-crm-dev.txt` (mismo patrón que `requirements-dev.txt`/
   `requirements-docs.txt`: todo con `==`) con `pytest`, `httpx` (requerido
   por `starlette.testclient.TestClient`, no declarado como dependencia de
   `fastapi`) fijados a las versiones ya verificadas localmente contra la
   suite real.
3. **Supply-chain**: extender `scripts/validate-supply-chain.ps1` para
   exigir también que `requirements-crm-dev.txt` tenga todas sus
   dependencias fijadas con `==`, igual criterio que los otros dos
   manifiestos ya cubiertos. Confirmar que el nuevo servicio Postgres del
   workflow no introduce ninguna acción `uses:` sin pin SHA (los
   contenedores de servicio se declaran por `image:`, no por `uses:`, así
   que no aplica, pero se verifica explícitamente).
4. **Test del propio circuito**: `tests/test_ci_workflow.py` tiene una
   aserción (`test_product_tests_job_has_placeholder_marker`) que asume
   literalmente que el marcador `PLACEHOLDER` sigue presente en
   `product-tests`. Se reemplaza esa aserción por una que verifique la
   forma real del job (Postgres de servicio, `pytest -v tests_crm/`,
   ausencia del marcador `PLACEHOLDER`), preservando el resto de
   aserciones sobre `circuit-tests`/`local-reconciler-tests` sin cambios.
   **Corrección detectada durante el build** (no prevista al escribir esta
   spec): existe un segundo archivo independiente,
   `tests/test_ci_integration.py::test_product_tests_is_placeholder`, con
   la misma suposición sobre el placeholder — descubierto recién al correr
   `pytest -v tests/` completo tras el cambio a `ci.yml` (falló
   `test_product_tests_is_placeholder[ci.yml]`, 266 passed / 1 failed).
   Se corrigió con el mismo criterio: la nueva
   `test_product_tests_runs_real_suite` verifica ausencia del marcador
   `PLACEHOLDER` y del step `Placeholder (sin stack definido)`, no la
   ausencia case-insensitive de la palabra "placeholder" en todo el
   archivo (el job conserva un comentario en prosa que la menciona para
   explicar por qué ya no aplica). El resto de `test_ci_integration.py` no
   cambia.
5. **Documentación**: `docs/tecnica/ci-real-product-tests.md` (nuevo)
   documentando la forma exacta del job, su relación con
   `docs/tecnica/ci-wiring-product-tests.md` heredado, y por qué el
   servicio Postgres del job no es ni sustituye al Postgres efímero de
   Docker usado en verificación manual ni al proyecto Supabase compartido.
   Par `docs/usuario/ci-real-product-tests.md` con la vista operativa
   (cómo leer un fallo de `product-tests` en una PR).
6. **Evidencia de release readiness**: ejecutar
   `scripts/release-readiness.ps1` (preflight read-only, no publica) contra
   el estado real y conservar su salida como evidencia; no se decide ni
   ejecuta ninguna release desde esta unidad.

## Explícitamente fuera de alcance

- Cualquier release, tag o publicación de `v0.1.0` (decisión humana
  aparte, fuera de esta unidad).
- La Unidad `08-persistencia-supabase-real` (requiere autorización humana
  explícita antes de iniciarse).
- Tocar `post-hitl-merge-gate.yml`, `post-merge-close-feature.yml` o
  `docs.yml`.
- Tocar `scripts/*.ps1` salvo `validate-supply-chain.ps1` (punto 3, dentro
  del alcance explícito de esta unidad por `ROADMAP.md`: "supply-chain").
- Configurar branch protection real en GitHub (setup manual, documentado
  aparte en `docs/tecnica/operational-readiness-docs.md`).
- Cualquier cambio de dominio en `gi_crm/`.

## Criterios de aceptación

1. `product-tests` en `.github/workflows/ci.yml` ya no contiene el
   marcador `PLACEHOLDER`; ejecuta `pytest -v tests_crm/` contra un
   servicio Postgres real dentro del job.
2. `pytest -v tests_crm/` en CI cubre las 66 pruebas de la suite (62 sin
   Postgres + 4 con `CRM_TEST_DATABASE_URL`), no sólo el subconjunto en
   memoria — verificable leyendo el log del run real de GitHub Actions.
3. `circuit-tests` (`pytest -v tests/`) sigue en verde sin regresiones,
   incluyendo el test reescrito de `test_ci_workflow.py`.
4. `local-reconciler-tests` sigue en verde sin cambios de alcance.
5. `scripts/validate-supply-chain.ps1` pasa localmente, cubriendo el nuevo
   `requirements-crm-dev.txt`.
6. `scripts/sync-agentic-adapters.ps1 -Check` pasa sin diferencias (esta
   unidad no toca `.agentic/`).
7. La PR de esta unidad muestra los tres jobs de CI (`circuit-tests`,
   `product-tests`, `local-reconciler-tests`) en verde de forma real
   (`gh pr checks`), no inferido.
8. `docs/tecnica/ci-real-product-tests.md` y su par en `docs/usuario/`
   existen y están enlazados desde los índices correspondientes.
9. `scripts/release-readiness.ps1` corrió contra el estado real de esta
   unidad y su salida queda documentada como evidencia (no se publica
   ninguna release).

## Supuestos y clarificaciones ya resueltas

- El "fuera de alcance" de `docs/tecnica/ci-wiring-product-tests.md"
  ("agregar build/test real de cualquier stack de producto") describe la
  feature histórica del template que introdujo el placeholder, no una
  restricción vigente para este repositorio derivado. `ROADMAP.md` de
  *este* repo asigna expresamente esa responsabilidad al ítem `07`. No es
  una contradicción material que requiera CLARIFY: ambas fuentes describen
  alcances de unidades distintas en repositorios distintos.
- El servicio Postgres de este job es efímero por ejecución de CI
  (contenedor de GitHub Actions), igual criterio que la verificación
  manual ya documentada en `test-report-1.md` con Docker local — nunca el
  proyecto Supabase compartido con Core/Persons.

## Riesgos

- Tiempo de arranque del servicio Postgres en el runner de GitHub Actions
  puede alargar el job `product-tests`; se mitiga con `health-cmd`/
  `health-retries` en la definición del servicio, patrón estándar de
  GitHub Actions.
- `httpx` no es dependencia declarada de `fastapi` en la versión usada
  (`0.141.1`); si no se fija explícitamente, `TestClient` fallaría en CI
  aunque pase localmente por tenerlo ya instalado en el entorno de
  desarrollo. Mitigado fijándolo en `requirements-crm-dev.txt`.
