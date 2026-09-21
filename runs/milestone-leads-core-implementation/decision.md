# Decisiones: Milestone leads-core-implementation (ítems 02–06)

## Alcance de esta unidad frente a `01-fundacion-diseno`

Todas las decisiones de arquitectura de fondo (ADR-C01 a ADR-C06) ya fueron
tomadas, revisadas y mergeadas en `01-fundacion-diseno`
(`docs/tecnica/arquitectura-crm.md`). Esta unidad no las reabre; las
implementa. Reabrirlas aquí sin evidencia nueva sería contradecir una
decisión ya vigente sin motivo material — no se hace.

## Por qué un solo Milestone para 02–06 y no 5 Features

Mismo criterio ya usado por GI-COMMON-PERSONS con su milestone 02-07,
documentado en `plan-crm.md`: los ítems 02–06 son interdependientes de
forma directa (el dominio no es revisable sin sus puertos; la persistencia
no es revisable sin el dominio que persiste; la API pública no es revisable
sin dominio y persistencia; el seguimiento multivertical extiende el mismo
dominio). Publicarlos como 5 PRs separadas dejaría contratos a medias
revisables de forma aislada sin sentido funcional completo. `ROADMAP.md`
los cierra atómicamente los 5 al mergear, según el manifest
`runs/milestone-leads-core-implementation/work-unit.json` ya creado por
`start-work-unit.ps1 -Mode Milestone`.

## Por qué no se reclasifica manualmente la profundidad SDD

`assess-work-unit.ps1` clasificó esta unidad como `HIGH`/`FULL`
(`score: 36`) sobre las rutas anticipadas del diff completo
(`gi_crm/*.py`, `supabase/migrations/0001_crm.sql`, `.github/workflows/
ci.yml`, etc.), evidencia en
`runs/milestone-leads-core-implementation/assess.jsonl`. Es la
clasificación correcta y esperable: hay persistencia con migración real,
cambio de gobernanza de CI (`product-tests` deja de ser placeholder), y
múltiples módulos de dominio nuevos. No se ajusta a mano ni se reduce a
STANDARD/LIGHT: `materialize-sdd.ps1` (evidencia en
`runs/milestone-leads-core-implementation/sdd.json`) deriva
`requiredArtifacts: [objective, spec, plan, tasks, decision,
validation-evidence, test-evidence, review, gates]` y este set de archivos
(`spec.md`, `plan.md`, `tasks.md`, este `decision.md`) responde
directamente a ese contrato.

## Contradicción resuelta: alcance de `product-tests` entre `plan-crm.md` y `ROADMAP.md`

`docs/tecnica/plan-crm.md` (unidad `01-fundacion-diseno`, sección "SDD, QA,
CI y HITL") dice: "El Milestone 02-06 debe sustituirlo [el placeholder de
`product-tests`] por una ejecución real de `tests_crm/` con Postgres de
servicio". `ROADMAP.md`, en cambio, asigna esa misma responsabilidad
explícitamente a `07-readiness-integracion`: "CI real (`product-tests` deja
de ser placeholder)". Ambas fuentes vienen de la misma unidad ya mergeada
y no pueden ser correctas a la vez para este Milestone.

Se resuelve a favor de `ROADMAP.md` sin bloquear la unidad, por dos
motivos concurrentes:

1. **Precedencia documental de `AGENTS.md`**: "ítems y referencias de
   `ROADMAP.md`" está por encima de un documento de plan técnico en la
   cadena de precedencia declarada ("instrucción humana vigente; reglas de
   este repositorio; ítems y referencias de `ROADMAP.md`; contexto de
   producto; arquitectura y ADRs; código y tests; supuestos explícitos").
2. **Precedente real y directo, no supuesto**: `gi-common-persons` (mismo
   patrón de ROADMAP, ítem `07-readiness-integracion` con idéntica
   descripción "CI real") mantuvo el placeholder de `product-tests` sin
   tocar durante todo su propio milestone de implementación (02-07) y lo
   reemplazó recién en su unidad `07-readiness-integracion` — verificado
   leyendo directamente `gi-common-persons/.github/workflows/ci.yml` (el
   placeholder sigue literal ahí) y su `ROADMAP.md` (`07-readiness-
   integracion` con los 8 ítems ya en `[x]`).

No es una contradicción de regla de negocio, permiso, dato o alcance
funcional del producto — es un desacuerdo de secuenciación entre un
documento de plan y el backlog canónico, resoluble por la propia jerarquía
de fuentes que define `AGENTS.md`, con evidencia directa corroborante. No
califica como "decisión material pendiente" que exija detenerse a
preguntar: `spec.md`/`plan.md`/`tasks.md` de esta unidad ya reflejan la
resolución (pruebas reales de Postgres locales/opcionales sí forman parte
de este Milestone; el reemplazo del job de CI de `product-tests` no).

## Fuera de alcance, explícitamente diferido

- **Migración SQL contra el Supabase compartido real**
  (`08-persistencia-supabase-real`): se implementa y prueba aquí sólo
  contra Postgres efímero (Docker local / servicio de CI). Desplegarla al
  proyecto compartido con Core/Persons requiere autorización humana previa
  a iniciar esa unidad, no sólo en su merge — decisión ya registrada en
  `ROADMAP.md` y `plan-crm.md`, no se adelanta aquí.
- **Verificación HTTP end-to-end con Core/Persons reales**: ninguno de los
  dos expone HTTP hoy (verificado en código, no supuesto). Los adaptadores
  se entregan y se prueban sólo contra servidor simulado; ningún artefacto
  de esta unidad declara esa integración como probada end-to-end.
- **`07-readiness-integracion` y el tag/release `v0.1.0`**: unidades y
  decisión humana separadas, posteriores al merge de este Milestone.

## Compatibilidad con Persons sin release propio

Se fija contra el commit de `develop` de `gi-common-persons` vigente al
iniciar la implementación real (ítem 02). Si Persons publica un cambio
incompatible en su propio `develop` antes de que este Milestone cierre, el
riesgo se resuelve actualizando el punto de compatibilidad dentro de la
misma unidad (no es una decisión nueva, es mantenimiento del supuesto ya
registrado en `plan-crm.md`), documentando el ajuste en este mismo archivo
si llega a ocurrir.

## Merge

Igual que en `01-fundacion-diseno` y `T01-fix-post-merge-close-mode`: el
agente no ejecuta el merge de la PR de este Milestone (bloqueado por el
clasificador de auto-aprobación del harness sobre evidencia que el propio
agente produjo). El humano decide MERGE/NO MERGE, vía
`complete-approved-pr.ps1 -GovernanceMode SingleMaintainer` o merge directo
en GitHub — ambos caminos ya usados y válidos en esta misma unidad de
trabajo de bootstrap, según `AGENTS.md`.
