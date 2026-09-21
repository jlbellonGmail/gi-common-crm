# Estado operativo de GI-COMMON-CRM

Fecha de inspección: 2026-09-20. Estado: unidad `01-fundacion-diseno` en
implementación, dentro de su worktree/rama propia; sin PR abierta todavía.

## Hechos

- `template-starter` v2.0.1 (snapshot commit `bfd363f`) adoptado sin
  historia/tags/releases/evidencia de origen. Commit inicial `92e50ad`.
- `gi-platform-core` `v0.1.0` (release publicado) y `gi-common-persons`
  (milestone 02-07 en `develop`, sin release) inspeccionados en su código
  real: ambos exponen sólo biblioteca Python, sin HTTP desplegado.
- Corrección aplicada en esta unidad: se eliminó la rama `main` creada
  prematuramente durante el bootstrap (sin release que la respaldara) y se
  fijó `develop` como rama por defecto del repositorio, conforme a la
  "Decisión: ciclo de vida de `main`" heredada del circuito.
- No se modificó Core, Persons, Template Starter ni ninguna vertical. No
  se tocó el proyecto Supabase compartido.
- Suite del circuito (`pytest -v tests/`): `267 passed, 2 warnings in
  394.60s` (los 2 warnings son ruido cosmético conocido de
  `test_agentic_evals.py` bajo Python 3.14/cp1252, no funcionales).
- No hay implementación de producto (`gi_crm`) todavía: es explícitamente
  el alcance del Milestone `leads-core-implementation` siguiente.

## Pendientes materiales

Ver "Clarificaciones materiales pendientes" en
[plan-crm.md](docs/tecnica/plan-crm.md): catálogo inicial de `LeadSource`
y motivos de cierre, nombres exactos de permisos `crm:lead:*`, y el riesgo
de fijar compatibilidad contra un commit de `develop` de Persons sin
release propio todavía.

## Próximo paso

Completar los artefactos SDD de `01-fundacion-diseno`
(`runs/01-fundacion-diseno/`), autoevaluación de QA/code-review y
`ready-for-pr.ps1` para dejarla en `READY_FOR_PR`. El HITL de merge sobre
esa PR es la siguiente decisión humana, no un paso automático.

<!-- STATUS:AUTO:BEGIN -->

## Estado verificado automáticamente

- Actualizado: 2026-09-21T02:10:34Z
- Versión: unreleased
- Rama: feature/01-fundacion-diseno
- HEAD: a076ea8c931e3c7b33a78032e3918618d353d22c
- Remoto: https://github.com/jlbellonGmail/gi-common-crm.git
- Working tree: dirty
- Worktrees: 2
- Worktrees Git: 2
- Unidades activas: = [feature/01-fundacion-diseno]
- PR activa: UNKNOWN / sin PR abierta
- CI: UNKNOWN / sin CI verificable
- CI vigente: UNKNOWN / sin CI verificable
- Última release: UNKNOWN / no disponible

<!-- STATUS:AUTO:END -->
