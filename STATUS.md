# Estado operativo de GI-COMMON-CRM

Fecha de inspección: 2026-09-21. Estado: unidad `01-fundacion-diseno`
cerrada (`[x]` en `ROADMAP.md`, PR #1 mergeada a `develop` con HITL
humano). Corrección de circuito `T01-fix-post-merge-close-mode` (PR #2)
también mergeada. Milestone `leads-core-implementation` (ítems 02–06) es
el próximo trabajo, todavía sin iniciar.

## Hechos

- `template-starter` v2.0.1 (snapshot commit `bfd363f`) adoptado sin
  historia/tags/releases/evidencia de origen. Commit inicial `92e50ad`.
- `gi-platform-core` `v0.1.0` (release publicado) y `gi-common-persons`
  (milestone 02-07 en `develop`, sin release) inspeccionados en su código
  real: ambos exponen sólo biblioteca Python, sin HTTP desplegado.
- Corrección aplicada en `01-fundacion-diseno`: se eliminó la rama `main`
  creada prematuramente durante el bootstrap (sin release que la
  respaldara) y se fijó `develop` como rama por defecto del repositorio,
  conforme a la "Decisión: ciclo de vida de `main`" heredada del circuito.
- PR #1 (`feature/01-fundacion-diseno`) mergeada a `develop` mediante
  HITL SingleMaintainer (`complete-approved-pr.ps1`, ejecutado
  personalmente por el humano al ser bloqueado el agente por el
  clasificador de auto-aprobación del harness).
- El workflow `post-merge-close-feature.yml` falló al cerrar
  `01-fundacion-diseno` en ROADMAP tras el merge de PR #1: la rama
  `feature/NN-slug` (sin versión) no emitía `mode=`/`branch=`, y
  `close-feature.ps1` recibía `-Mode ''` inválido (run `35556510071`,
  job `106201062447`). Corregido en la unidad Maintenance auxiliar
  `T01-fix-post-merge-close-mode` (PR #2, mergeada directamente en
  GitHub por el humano tras CI verde). Detalle en
  [post-merge-close-mode-fix.md](docs/tecnica/post-merge-close-mode-fix.md).
- Cierre de `01-fundacion-diseno` completado aparte, invocando
  `close-feature.ps1` directamente contra la PR #1 ya mergeada (sin
  repetir el merge), tras confirmar que la corrección del workflow no se
  ejercitaba con el propio merge de PR #2 (rama `maintenance/` sin
  versión, cae en el `else`/skip documentado como incidencia).
- No se modificó Core, Persons, Template Starter ni ninguna vertical. No
  se tocó el proyecto Supabase compartido.
- Suite del circuito (`pytest -q tests/`): `267 passed, 2 warnings` en
  múltiples corridas (los 2 warnings son ruido cosmético conocido de
  `test_agentic_evals.py` bajo Python 3.14/cp1252, no funcionales).
- No hay implementación de producto (`gi_crm`) todavía: es explícitamente
  el alcance del Milestone `leads-core-implementation` siguiente.

## Pendientes materiales

Ver "Clarificaciones materiales pendientes" en
[plan-crm.md](docs/tecnica/plan-crm.md): catálogo inicial de `LeadSource`
y motivos de cierre, nombres exactos de permisos `crm:lead:*`, y el riesgo
de fijar compatibilidad contra un commit de `develop` de Persons sin
release propio todavía.

Incidencia conocida, no bloqueante: `maintenance/TNN-slug` sin prefijo de
versión (soportado por `Get-MaintenanceIdentity`) no está reconocido por
`post-merge-close-feature.yml`, que sólo acepta
`maintenance/vX.Y.Z-TNN-slug`. Cae en el `else`/skip, no falla. Ver
`docs/tecnica/post-merge-close-mode-fix.md`.

Incidencia conocida, no bloqueante (detectada al intentar la limpieza
local de `T01-fix-post-merge-close-mode`): `local-feature-reconcile.ps1`
no tiene ninguna noción de alcance "auxiliar" de Maintenance (a
diferencia de `close-feature.ps1`, que sí resuelve
`Resolve-MaintenanceScope`); espera incondicionalmente un `[x]` en
`ROADMAP.md` para el slug dado, que nunca existe para una unidad
Maintenance auxiliar, y termina en `Timeout esperando cierre remoto`. La
limpieza de los worktrees de `01-fundacion-diseno` y
`T01-fix-post-merge-close-mode` se completó igual: la primera vía el
propio reconciliador (unidad con ítem real en ROADMAP), la segunda de
forma manual (`git worktree remove` + `git branch -d`) tras confirmar por
`gh pr view` que la PR #2 estaba `MERGED`. No se creó una unidad nueva
para corregir `local-feature-reconcile.ps1`: es limpieza local, de menor
severidad, sin impacto en CI ni en el estado publicado de `develop`;
queda registrada aquí para una corrección futura si se decide automatizar
Maintenance auxiliar en ese script también.

## Próximo paso

Iniciar el Milestone `leads-core-implementation` (ítems 02–06:
contratos-integracion, dominio-leads, persistencia-aislamiento,
api-publica, seguimiento-multivertical) vía `start-work-unit.ps1 -Mode
Milestone`, según el plan de arquitectura ya documentado en
`docs/tecnica/arquitectura-crm.md` y `docs/tecnica/plan-crm.md`.

Nota manual sobre el bloque automático siguiente: `Worktrees`/`Worktrees
Git` no reflejan el conteo real cuando hay exactamente 1 worktree
(`Get-Worktrees` en `update-status.ps1` aplana el único `OrderedDictionary`
resultante en sus 3 valores escalares al pasar por `return @($result)` —
gotcha conocido de PowerShell con arrays de un solo elemento enumerable).
Verificado con `git worktree list --porcelain`: 1 worktree real
(`gi-common-crm` en `develop`) al momento de este cierre. Es un defecto
cosmético del propio contador, no del estado real ni de ningún gate;
no se corrige en esta unidad por alcance.

<!-- STATUS:AUTO:BEGIN -->

## Estado verificado automáticamente

- Actualizado: 2026-09-21T04:07:29Z
- Versión: unreleased
- Rama: develop
- HEAD: 5e5649e95b1de08a766cda8c37adcd5aba7484b7
- Remoto: https://github.com/jlbellonGmail/gi-common-crm.git
- Working tree: dirty
- Worktrees: 3
- Worktrees Git: 3
- Unidades activas: ninguna
- PR activa: UNKNOWN / sin PR abierta
- CI: UNKNOWN / sin CI verificable
- CI vigente: UNKNOWN / sin CI verificable
- Última release: UNKNOWN / no disponible

<!-- STATUS:AUTO:END -->
