# 01-fundacion-diseno — fundación documental y arquitectura de CRM

Estado: EN_REVISIÓN
Versión: v2.0.1 (circuito)
Tipo: Feature
SDD: LIGHT
PR: no creada
Merge: no realizado

## Objetivo

Consolidar la fundación documental, procedencia y contratos reales de
Core/Persons, la arquitectura del dominio CRM y el plan de las unidades
siguientes, con revisión independiente, antes de implementar producto.

## Resultado

El bootstrap (`92e50ad`) y el backlog/contexto de producto (`a076ea8`) ya
estaban en `develop`. Esta unidad agrega la arquitectura de producto
(`arquitectura-crm.md`), una nueva decisión en `arquitectura.md`, el plan
de unidades (`plan-crm.md`) y adapta `README.md`/`STATUS.md`. ASSESS
determinista clasificó el alcance como `LOW` / `LIGHT`.

## Cambios principales

- `docs/tecnica/arquitectura.md`: nueva sección "Decisión: fundación de
  GI-COMMON-CRM", sin reescribir el historial heredado del circuito.
- `docs/tecnica/arquitectura-crm.md` (nuevo): ADR-C01 a ADR-C06 —
  cardinalidad Lead↔Person↔Organization, stack/composición, autorización
  y multitenancy fail-safe, persistencia Postgres sin ORM, modalidad HTTP
  con Core/Persons documentada como bloqueada, ciclo de vida comercial.
- `docs/tecnica/plan-crm.md` (nuevo): descomposición de unidades con
  aceptación comprobable, matriz mínima de pruebas y clarificaciones
  materiales pendientes.
- `README.md`/`STATUS.md`: reescritos para reflejar el producto real y su
  estado actual (fundación, sin implementación de `gi_crm` todavía).
- Corrección de gobernanza sobre el repositorio remoto: se eliminó la rama
  `main` creada prematuramente durante el bootstrap (antes de cualquier
  release) y se fijó `develop` como rama por defecto, conforme a la
  "Decisión: ciclo de vida de `main`" heredada del circuito.

## Validación

- `pytest -q tests/`: primera corrida `2 failed, 265 passed, 2 warnings en
  273.89s`; ambos fallos (`test_close_feature_script.py::
  test_pr_merged_into_another_base_stops_without_cleanup` y
  `::test_push_failure_does_not_cleanup_or_claim_success`) fallan por un
  error de permisos de Windows al escribir objetos Git en un remoto de
  prueba local (`unable to write file ... Permission denied`), no
  relacionado con el diff de esta unidad (sólo documentación). Reejecutados
  en aislamiento: `2 passed in 5.37s`. Corrida completa repetida para
  evidencia limpia: `267 passed, 2 warnings in 338.33s`. Se registran los
  2 fallos iniciales como flake conocido del entorno Windows (contención de
  E/S al escribir objetos Git en remotos de prueba locales), no como
  regresión introducida aquí.
- `check-integrity.ps1`: PASS.
- `check-status.ps1`: PASS (warning esperado: `gh` no resuelto desde el
  PATH de `pwsh` en esta sesión; PR/CI no verificables desde el script,
  verificados por separado con `gh` desde bash antes de pedir HITL).
- `sync-agentic-adapters.ps1 -Check`: adaptadores sincronizados.
- `validate-supply-chain.ps1`: OK (5 workflows, acciones SHA-pinned,
  permisos explícitos, dependencias fijadas).
- `assess-work-unit.ps1`: PASS, `LOW` / `LIGHT`.
- `materialize-sdd.ps1`: PASS, SDD adaptativo `LIGHT`.

## Decisiones

- `person_id` en Lead es opcional y sin `UNIQUE` (ADR-C01), confirmado por
  el GOAL, sin necesidad de confirmación humana adicional.
- La integración HTTP con Core y Persons queda documentada como bloqueada
  (ADR-C05): ninguno de los dos expone HTTP hoy; sólo se prepara el
  adaptador contra un contrato documentado, probado sólo con simulador.
- Persistencia Postgres sin ORM, esquema `crm.*`, misma convención que
  Persons (ADR-C04); pruebas reales sólo contra Postgres efímero, nunca
  contra el proyecto Supabase compartido de Core/Persons.
- `main` no se recrea en esta unidad: queda condicionada a la decisión y
  ejecución humana del primer release (`v0.1.0`).

## Incidencias

- Persons no tiene release/tag propio todavía (milestone 02-07 en
  `develop`): se registra como riesgo de fundación movediza para el
  Milestone `leads-core-implementation` si Persons publica cambios
  incompatibles antes de que CRM alcance su propio release.
- Catálogo inicial de `LeadSource`/motivos de cierre y nombres exactos de
  permisos `crm:lead:*` quedan como decisiones de diseño de `02` y `03`,
  no de esta unidad.

## Detalle

La unidad no declara implementación funcional ni readiness de producto.
Su revisión valida procedencia, límites de responsabilidad frente a
Core/Persons/verticales, ausencia de dependencias inversas, y que los
bloqueos (HTTP, Supabase compartido) queden derivados a unidades
posteriores en vez de resueltos por invención.
