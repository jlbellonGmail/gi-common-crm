```yaml
status: approved
attempt: 1
feedback: []
```

# Code review — 07-readiness-integracion

## Alcance revisado

Diff vigente sobre `develop` en la rama `feature/07-readiness-integracion`
(sin commitear todavía): `.github/workflows/ci.yml` (job `product-tests`
reescrito), `scripts/validate-supply-chain.ps1` (extendido a
`requirements-crm-dev.txt`), `requirements-crm-dev.txt` (nuevo),
`tests/test_ci_workflow.py` y `tests/test_ci_integration.py` (ambos con
su aserción de placeholder reescrita), `docs/tecnica/readiness-
integracion.md` + `docs/usuario/readiness-integracion.md` (nuevos,
enlazados vía `update-doc-indexes.ps1`), y `runs/07-readiness-
integracion/*` (evidencia).

## Verificación contra criterios de aceptación de `spec.md`

1. **`product-tests` sin `PLACEHOLDER`, corre Postgres real** — confirmado
   leyendo `.github/workflows/ci.yml`: servicio `postgres:16-alpine` con
   health-check, instalación vía extras `[http,postgres]` +
   `requirements-crm-dev.txt`, `pytest -v tests_crm/` con
   `CRM_TEST_DATABASE_URL`. Sin `continue-on-error`.
2. **Cobertura de las 66 pruebas en CI** — el job corre `pytest -v
   tests_crm/` sin filtro de archivo ni marcador, mismo alcance que la
   corrida local (62 + 4). Confirmable en el run real de GitHub Actions
   una vez abierta la PR (criterio 7, todavía pendiente).
3. **`circuit-tests` sin regresiones** — `pytest -v tests/`: 267 passed
   (`test-report-1.md`), incluye los dos archivos de test reescritos.
4. **`local-reconciler-tests` sin cambios de alcance** — confirmado: el
   diff no toca ese job ni `tests/test_local_reconciler_scripts.py`.
5. **`validate-supply-chain.ps1` cubre el manifiesto nuevo** — confirmado
   por lectura directa del script (línea con el array de tres
   manifiestos) y por la corrida real (`Supply chain OK`).
6. **`sync-agentic-adapters.ps1 -Check` sin diferencias** — confirmado
   (`Adaptadores agenticos sincronizados`); coherente con que esta unidad
   no toca `.agentic/`.
7. **CI real verde en la PR** — pendiente hasta abrir la PR; no se marca
   como cumplido acá (evita inferir un resultado no observado).
8. **Documentación enlazada** — confirmado:
   `docs/tecnica/readiness-integracion.md` y su par de usuario existen,
   con contenido real (forma exacta del job, procedimiento de
   reproducción local, relación con el placeholder heredado), y quedan
   enlazados en ambos índices vía el mecanismo oficial
   (`update-doc-indexes.ps1`), sin edición manual de los marcadores
   `FEATURE_LINKS`.
9. **`release-readiness.ps1` documentado** — confirmado en
   `release-readiness.md`: rechazo real y esperado, con el motivo preciso
   (script parametrizado para el ROADMAP/tag histórico de
   `template-starter`, no de este repositorio) registrado como hallazgo,
   no ocultado ni forzado a pasar artificialmente.

## Otros hallazgos

- El nombre real de los documentos (`readiness-integracion.md`, derivado
  de `Get-WorkUnitInfo -Mode Feature` para el slug de esta unidad) difiere
  del nombre libre (`ci-real-product-tests.md`) con el que se redactaron
  inicialmente en `plan.md`; se corrigió el nombre de archivo y todas las
  referencias cruzadas (el propio contenido, `tests/test_ci_workflow.py`,
  `tests/test_ci_integration.py`) antes de enlazarlos, sin dejar un
  archivo huérfano ni una referencia rota. Mismo tipo de corrección que ya
  ocurrió en el Milestone previo con el mismo mecanismo.
- `requirements-crm-dev.txt` no duplica `fastapi`/`pydantic`/`psycopg`
  (ya fijados por rango en los extras de `pyproject.toml`, ADR-C02):
  correcto, evita dos fuentes de verdad sobre la misma dependencia (ver
  `decision.md`).
- El hallazgo sobre `tests/test_ci_integration.py` (segundo test con la
  misma suposición, no anticipado en `spec.md`) está documentado con
  transparencia en `spec.md` (sección de alcance, punto 4) y en
  `test-report-1.md`, no oculto ni minimizado.
- El hallazgo sobre `scripts/release-readiness.ps1` (parametrizado para el
  historial de `template-starter`, inutilizable tal cual para `v0.1.0` de
  `gi-common-crm`) queda registrado como pendiente de decisión humana en
  `release-readiness.md`, sin que esta unidad invente la política de
  release de este proyecto (fuera de su alcance declarado).

## Veredicto

Sin hallazgos bloqueantes. La evidencia es proporcional a `FULL` (cambio
de gate obligatorio de CI, dos correcciones reales detectadas y resueltas
durante el build, documentación completa). La unidad puede pasar a
`ready-for-pr.ps1` una vez commiteado el diff vigente.
