# Decisiones: Feature 07-readiness-integracion

## Por qué esta unidad sí toca `.github/workflows/ci.yml` y
`scripts/validate-supply-chain.ps1`

`AGENTS.md` (sección "Configuración de modelos") y varios documentos
heredados del template (`docs/tecnica/ci-wiring-product-tests.md`) tratan
los workflows y scripts del circuito como superficie sensible que un
agente no debería tocar livianamente. Eso sigue vigente para
`post-hitl-merge-gate.yml`, `post-merge-close-feature.yml`, `docs.yml` y el
resto de `scripts/*.ps1` — ninguno de ellos se toca en esta unidad. Pero
`ROADMAP.md` de este repositorio (no del template) asigna expresamente el
reemplazo del placeholder de `product-tests` y el trabajo de
"supply-chain" al ítem `07-readiness-integracion`: "CI real (product-tests
deja de ser placeholder), documentación completa, supply-chain, evidencia
para HITL de release". Por la cadena de precedencia de `AGENTS.md`
("ítems y referencias de `ROADMAP.md`" está por encima de un documento de
plan/arquitectura), este ítem es la autorización explícita para tocar
exactamente esos dos archivos, y sólo esos, dentro del alcance descrito.

## Por qué el "fuera de alcance" de `ci-wiring-product-tests.md` no bloquea

Ese documento (heredado sin cambios del snapshot de `template-starter`)
dice que "agregar build/test real de cualquier stack de producto" queda
fuera de alcance de la feature que introdujo el placeholder
(`04-ci-wiring-product-tests`). Es una decisión correcta para *esa*
feature en *ese* repositorio (el template no tiene stack propio). No es
una restricción vigente para `gi-common-crm`, que ya fijó su stack
(`arquitectura-crm.md`, ADR-C02) y cuyo propio `ROADMAP.md` asigna
expresamente esta tarea a esta unidad. No se trata como contradicción
material que requiera CLARIFY: ambos documentos son correctos para el
alcance que describen, y no se reescribe el documento heredado (registro
histórico de una decisión de otro repositorio en el origen).

## Por qué `requirements-crm-dev.txt` en vez de sumar a `requirements-dev.txt`

`requirements-dev.txt` documenta explícitamente en su propio comentario
que es "para correr los tests del circuito (scripts/*.ps1)" — no del
producto. Mezclar ahí las dependencias de `tests_crm/` (`pytest` ya está
duplicado, `httpx` no tiene nada que ver con el circuito) confundiría esa
frontera ya declarada. Un manifiesto propio, mismo formato y mismo
criterio de fijación (`==`), preserva la separación y es lo que
`scripts/validate-supply-chain.ps1` ya sabe generalizar con un cambio
mínimo (Paso 2 de `plan.md`).

## Por qué no se agrega `fastapi`/`pydantic`/`psycopg` a `requirements-crm-dev.txt`

Esos tres ya están fijados por rango en los extras `[http]`/`[postgres]`
de `pyproject.toml` (ADR-C02, ya mergeado). Declararlos de nuevo con `==`
en un manifiesto aparte crearía dos fuentes de verdad sobre la misma
dependencia que podrían divergir. El paso de instalación de CI usa
`pip install -e ".[http,postgres]"` (misma fuente que un consumidor real
de la biblioteca usaría) y sólo el manifiesto nuevo fija lo que es
exclusivo de la suite de tests, no de la biblioteca en sí.

## Por qué no se reclasifica la profundidad SDD

`assess-work-unit.ps1` clasificó `HIGH`/`FULL` sobre las rutas de este
diff (`.github/workflows/ci.yml` cae en la señal `automation-or-
governance`, peso alto) — evidencia en `runs/07-readiness-integracion/
assess.jsonl`. Es correcto: un cambio de gate obligatorio de CI es
gobernanza real, no documentación de bajo riesgo, aunque el resto del diff
(tests, docs) sea de riesgo bajo. No se ajusta a mano.
