# GI-COMMON-CRM

Módulo COMMON, independiente y multitenant de gestión de Leads y su ciclo
de vida comercial para el Sistema Integral GI. Reutilizable por N
verticales (Dental, Law, GI-OT, futuras) sin que ninguna duplique la
capacidad de Leads ni CRM incorpore reglas propias de una vertical.

Estado actual: **fundación y diseño** (unidad `01-fundacion-diseno`). No
existe todavía implementación de `gi_crm` (paquete Python, esquema SQL,
API HTTP): esta unidad deja establecidos la arquitectura, los límites de
responsabilidad frente a `gi-platform-core`/`gi-common-persons`/verticales,
el modelo de dominio de Lead y el plan de las unidades siguientes. La
implementación funcional se ejecuta en el Milestone
`leads-core-implementation` (ítems `02` a `06` del [ROADMAP](ROADMAP.md)).

## Límites de responsabilidad

- **gi-platform-core**: organizaciones, sedes, identidad de acceso,
  autenticación, autorización, multitenancy. CRM consume su superficie
  pública (`CoreApi.authorize`), nunca la duplica.
- **gi-common-persons**: personas físicas, identificadores, contacto,
  resolución/deduplicación. Fuente autorizada de datos de personas; CRM no
  implementa un sistema paralelo.
- **gi-common-crm** (este repo): Leads, origen/canal de captación, ciclo
  de vida comercial, asignación de responsables, actividades y
  seguimiento, historial comercial, conversión y cierre.
- **Verticales**: sólo sus especializaciones propias (p. ej. Patient en
  Dental). Consumen los contratos públicos de Core/Persons/CRM.

Detalle completo: [contexto de producto](docs/producto/contexto-producto.md),
[arquitectura del circuito](docs/tecnica/arquitectura.md) y
[arquitectura de CRM](docs/tecnica/arquitectura-crm.md).

## Integración real verificada (no supuesta)

`gi-platform-core` (`v0.1.0`) y `gi-common-persons` (milestone 02-07 en
`develop`, sin release todavía) exponen hoy **sólo biblioteca Python**; no
hay servicio HTTP desplegado para ninguno de los dos. CRM está diseñado
para operar mediante puertos locales (`Protocol`) en Modalidad Biblioteca
desde el Milestone `leads-core-implementation`; la Modalidad HTTP con
Core/Persons queda documentada y explícitamente marcada como bloqueada
hasta que esos servicios existan.

## Plan de trabajo

- [Plan de unidades](docs/tecnica/plan-crm.md) — descomposición, aceptación
  y matriz de pruebas por unidad.
- [ROADMAP](ROADMAP.md) — backlog y estado (`[ ]`/`[-]`/`[x]`).

## Circuito operativo

El circuito procede del Template GI v2.0.1 (snapshot sin historia, tags ni
releases de origen). Su operación (roles, work units, PR, HITL) está en
[AGENTS.md](AGENTS.md); el estado para reentrada, en [STATUS.md](STATUS.md).
