# Estado operativo de GI-COMMON-CRM

Fecha de inspección: 2026-09-21. Estado: unidad `01-fundacion-diseno`
cerrada (`[x]` en `ROADMAP.md`, PR #1 mergeada a `develop` con HITL
humano). Corrección de circuito `T01-fix-post-merge-close-mode` (PR #2)
también mergeada. **Milestone `leads-core-implementation` (ítems 02–06)
mergeado a `develop` mediante PR #3** (autorización humana directa,
`merge commit 93b8d68`, confirmado vía `gh pr view 3` → `state: MERGED`).
`post-merge-close-feature.yml` cerró los 5 ítems a `[x]` en `ROADMAP.md`
(commit `195da32`) y sincronizó `STATUS.md` (commit `d2af72f`) sin
intervención manual — verificado con `gh run list --workflow=post-merge-
close-feature.yml` (`conclusion: success` sobre
`milestone/leads-core-implementation`). Worktree y rama local reconciliados
vía `local-feature-reconcile.ps1` (rama remota `milestone/leads-core-
implementation` seguía existiendo porque el merge humano no incluyó
`--delete-branch`; sólo se limpió el estado local, no se tocó el remoto).
`pytest -q tests/` (circuito): `267 passed, 2 warnings`. `pytest -q
tests_crm/` (producto): `62 passed, 4 skipped` (Postgres real no
configurado localmente). En curso: Unidad `07-readiness-integracion`.

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
- **Milestone `leads-core-implementation` implementado y evidenciado**:
  paquete `gi_crm/` completo, migración `supabase/migrations/
  20260921000100_crm.sql`, `tests_crm/` (62 passed, 4 skipped sin
  Postgres real; 4 passed adicionales verificados manualmente contra un
  contenedor `postgres:16-alpine` efímero, no el Supabase compartido).
  `pytest -q tests/` del circuito: 267 passed. SDD FULL completo
  (`SUMMARY.md`, `audit-1.md`, `test-report-1.md`, `code-review-1.md`).
  `ready-for-pr.ps1` corrió con éxito: los 5 ítems quedaron `[-]` en
  `ROADMAP.md` y se abrió **PR #3** contra `develop`. CI verde confirmado
  en múltiples commits (`gh pr checks 3`).
- **Bug real corregido en `.github/workflows/post-hitl-merge-gate.yml`**:
  el step "Completar PR aprobada si CI esta verde" declaraba `shell: pwsh`
  pero su cuerpo usaba sintaxis bash (`if [[ ]]`), lo que producía un
  `ParserError` real en cada ejecución (confirmado vía `gh run view
  --log` en el run `35599287407` de la PR #3). Corregido reescribiendo el
  step en PowerShell válido, sin tocar ninguna validación de autorización
  ni el contrato `SingleMaintainer` existente. De paso se corrigió un
  desajuste de rutas: las tres evidencias
  (`-AuthorizationPath`/`-IndependentReviewPath`/`-IntegrityEvidencePath`)
  se calculaban como `runs/<slug>/...` para todos los modos, pero
  `Get-WorkUnitInfo -Mode Milestone` usa `runs/milestone-<slug>/`.
  Verificado en runs reales posteriores (`35603454628`, `35604073682`):
  el step ahora corre sin error de sintaxis y falla de forma controlada
  con `"No existe la autorizacion previa requerida:
  runs/milestone-leads-core-implementation/human-authorization.md"` —
  el gate real de autorización, no un crash. Sin regresiones en CI.
- **Recompatibilización con `gi-platform-core v0.2.1`** (tag real
  inspeccionado, no supuesto) y con el `develop` actual de
  `gi-common-persons`: `CoreApi.authorize()` y el subset de `PersonsApi`
  usado por CRM no cambiaron de forma desde la verificación original;
  compatibles sin ajustes de código. Hallazgo nuevo: Core `v0.2.1` agregó
  un adaptador HTTP propio (`gi_platform_core/http.py`), inexistente en
  `v0.1.0`, pero sólo cubre `identity-validation`/`identity-links`
  (vinculación Core↔Persons) — no existe ninguna ruta `/v1/authorize`.
  `CoreHttpApi` de `gi_crm` sigue bloqueado end-to-end por esa razón
  específica, no por ausencia total de servicio HTTP en Core. Persons
  sigue sin exponer ningún módulo HTTP. Documentación actualizada en
  `docs/tecnica/contratos-integracion.md` y en los docstrings de
  `gi_crm/adapters/core_http.py`/`persons_http.py` (que además
  referenciaban un nombre de archivo obsoleto, corregido de paso).
- PR #3 mergeada por decisión humana explícita, comunicada directamente en
  el chat de este circuito (no vía comentario en GitHub) y verificada
  después contra el estado real (`gh pr view 3`, `git log origin/develop`,
  `ROADMAP.md`), no asumida. No se usó el mecanismo automatizado
  `GovernanceMode SingleMaintainer` de `complete-approved-pr.ps1`: este
  agente no fabricó `human-authorization.md`/`independent-review.md`
  porque el propio diseño del script exige que la revisión independiente
  no sea self-review del Builder, y este agente fue el único Builder de
  todo el Milestone.
- **Hallazgo real, no relacionado con esta unidad, registrado por
  precisión**: `decision.md` del Milestone (ya mergeado) afirma que
  `gi-common-persons` "reemplazó" el placeholder de `product-tests` en su
  propia unidad `07-readiness-integracion`, citando su `ci.yml` como
  verificación. Reinspeccionado ahora contra el `develop` real de
  `gi-common-persons` (commit `433b651`): el placeholder sigue **literal**
  en `product-tests` pese a que `ROADMAP.md` de ese repo marca
  `07-readiness-integracion` como `[x]`. La afirmación era incorrecta;
  no se corrige `gi-common-persons` desde aquí (fuera de alcance y
  prohibido por el GOAL). No invalida la decisión tomada en su momento
  (la razón principal era la precedencia de `ROADMAP.md` sobre
  `plan-crm.md` según `AGENTS.md`, independiente de este precedente), pero
  sí significa que la Unidad `07` de CRM no tiene, en la práctica, un
  ejemplo real que copiar de un repo hermano — el CI real de
  `product-tests` se diseña aquí desde cero.

## Pendientes materiales

Ninguno bloqueante para continuar. El único pendiente de gobernanza
(cierre de la PR #3) se resolvió con la acción humana descrita arriba.

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

1. Milestone `leads-core-implementation` cerrado. Continuar autónomamente
   con la Unidad `07-readiness-integracion`: reemplazar el placeholder de
   `product-tests` por ejecución real de `tests_crm/` contra Postgres de
   servicio, completar documentación de integración/supply-chain y dejar
   evidencia para el próximo HITL (PR de la unidad 07).
2. La Unidad `08-persistencia-supabase-real` permanece explícitamente
   diferida hasta autorización humana adicional; no se inicia en esta
   unidad.

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

- Actualizado: 2026-09-25T14:38:27Z
- Versión: unreleased
- Rama: develop
- HEAD: fad7ba372e11008b800e647ba43a039e891a02a4
- Remoto: https://github.com/jlbellonGmail/gi-common-crm.git
- Working tree: dirty
- Worktrees: 3
- Worktrees Git: 3
- Unidades activas: ninguna
- PR activa: UNKNOWN / sin PR abierta
- CI: failure @ fad7ba372e11008b800e647ba43a039e891a02a4
- CI vigente: failure @ fad7ba372e11008b800e647ba43a039e891a02a4
- Última release: UNKNOWN / no disponible

<!-- STATUS:AUTO:END -->
