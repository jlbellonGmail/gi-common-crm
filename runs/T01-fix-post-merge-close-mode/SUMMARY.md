Estado: READY_FOR_PR
Versión: sin versión (Maintenance auxiliar, sin ítem propio en ROADMAP)
Tipo: Maintenance
SDD: FULL
PR: pendiente de apertura
Merge: pendiente de HITL (SingleMaintainer)

## Objetivo

Corregir `.github/workflows/post-merge-close-feature.yml` para que las
ramas `feature/NN-slug` sin prefijo de versión (interfaz legacy
documentada en `AGENTS.md`) completen el cierre automático de ROADMAP en
vez de fallar por `-Mode ''` inválido en `close-feature.ps1`.

## Resultado

Corrección aplicada y validada localmente (YAML, simetría de las cuatro
ramas de la condición, suite completa del circuito). Unidad lista para
PR contra `develop`; el cierre pendiente de `01-fundacion-diseno` se
completa aparte, directamente contra la PR #1 ya mergeada.

## Cambios principales

- `.github/workflows/post-merge-close-feature.yml`: se agregaron
  `echo "branch=$head_ref"` y `echo "mode=Feature"` a la rama `elif` que
  reconoce `feature/NN-slug` sin versión, igualándola a las otras tres
  ramas de la misma condición (`feature/vX.Y.Z-NN-slug`, `milestone/slug`,
  `maintenance/vX.Y.Z-TNN-slug`).
- `docs/tecnica/post-merge-close-mode-fix.md`: nota técnica del defecto,
  la evidencia real que lo confirma y la incidencia relacionada dejada
  fuera de alcance.

## Validación

- YAML válido (`yaml.safe_load`).
- Simetría de las cuatro ramas de la condición confirmada por inspección
  directa del archivo.
- `pytest -q tests/` (suite del circuito), dos corridas: 267 passed en
  ambas (412.33s y 419.16s), exit code 0 confirmado en la segunda corrida
  con captura explícita de `$LASTEXITCODE`. Ver `test-report-1.md`.
- No se corrió el workflow en GitHub Actions todavía; se ejercitará
  realmente cuando el cierre de `01-fundacion-diseno` invoque el flujo
  correspondiente (ver "Incidencias").

## Decisiones

Ver `decision.md`: alcance limitado a la emisión de outputs del paso de
derivación de slug/modo; no se toca `close-feature.ps1` ni el guard de
`develop`; se publica como unidad `Maintenance` auxiliar siguiendo el
precedente real de `gi-platform-core` (`04-post-merge-close-dispatch`);
el `docs/tecnica/` nuevo no se enlaza en `docs/tecnica/index.md` porque
`Get-WorkUnitInfo -Mode Maintenance` resuelve esos índices como `$null` y
no existe una interfaz oficial equivalente a
`scripts/update-doc-indexes.ps1` para Maintenance.

## Incidencias

- La propia PR de esta unidad se mergea desde una rama `maintenance/`
  sin versión, que el workflow corregido todavía no reconoce (incidencia
  relacionada, documentada como fuera de alcance en `spec.md`): su propio
  merge no ejercitará la rama de código corregida. El cierre de
  `01-fundacion-diseno` se completa por eso mediante invocación directa
  de `close-feature.ps1`, no esperando a que el workflow se dispare.
- El workflow corregido en sí no se ejecutó todavía en GitHub Actions
  contra una rama `feature/NN-slug` real después del fix; queda como
  validación pendiente en producción, igual que cualquier cambio a
  `.github/workflows/` en este circuito.

## Detalle

Ver `spec.md`, `plan.md`, `tasks.md`, `decision.md`, `audit-1.md`,
`test-report-1.md`, `code-review-1.md` en este mismo directorio, y
`docs/tecnica/post-merge-close-mode-fix.md` para el detalle técnico
completo con referencias exactas al run/job de GitHub Actions que
evidenció el defecto.
