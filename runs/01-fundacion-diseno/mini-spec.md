# Mini-spec — 01-fundacion-diseno

## Alcance

Validar la fundación documental de GI-COMMON-CRM: procedencia real desde
`template-starter` (no desde `template`, el repositorio histórico
prohibido), límites de dominio frente a `gi-platform-core`,
`gi-common-persons` y las verticales, contratos reales verificados (no
supuestos) de Core y Persons, arquitectura y cardinalidad del dominio Lead,
plan de unidades siguientes y corrección del ciclo de vida de la rama
`main`.

## Invariantes verificables

1. `gi-common-crm` no importa `gi_platform_core` ni `gi_persons`: define
   sus propios puertos locales (`Protocol`), a diseñar en `02-contratos-
   integracion`. Esta unidad no introduce código de producto, sólo
   documenta la decisión (ADR-C02 en `arquitectura-crm.md`).
2. `person_id` en Lead queda documentado como opcional y sin `UNIQUE`
   (ADR-C01), consistente con la confirmación explícita del GOAL.
3. La integración HTTP con Core y Persons se documenta como bloqueada
   (ADR-C05): ninguna afirmación de esta unidad declara esa integración
   disponible o verificada.
4. `main` no existe en el repositorio remoto al cierre de esta unidad: se
   eliminó la creada prematuramente durante el bootstrap y se dejó
   `develop` como rama por defecto, conforme a la decisión de ciclo de
   vida heredada del circuito.
5. Ningún archivo de `gi-platform-core`, `gi-common-persons`,
   `template-starter` ni de una vertical fue modificado.

## Fuentes y límites

Fuentes: el GOAL recibido el 2026-09-20, el código real de
`gi-platform-core` (`gi_platform_core/contracts.py`, release `v0.1.0`) y
`gi-common-persons` (`gi_persons/api.py`, `ports.py`, `models.py`,
`errors.py`, `dbapi.py`, migraciones SQL, `docs/tecnica/arquitectura.md` y
`arquitectura-persons.md` como precedente estructural), y el propio
`template-starter` (snapshot commit `bfd363f`, circuito v2.0.1). No se
infieren capacidades HTTP de Core/Persons no observadas en su código, ni
catálogos de país/documento, ni reglas de retención o contenido legal no
provistos por el GOAL.

## Criterio de salida

Suite del circuito en verde (`pytest -v tests/`), revisión de código
propia (code-review) aprobada sobre el diff de esta unidad, y unidad lista
para `ready-for-pr.ps1` — el Milestone `leads-core-implementation`
(`02` a `06`) sólo se inicia después del cierre normal (PR + HITL de
merge) de esta unidad, no antes.
