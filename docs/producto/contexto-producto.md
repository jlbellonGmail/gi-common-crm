# Contexto de producto — GI-COMMON-CRM

Fuente: GOAL "GI-COMMON-CRM — Fundación, diseño e implementación" recibido
el 2026-09-20. Documento transversal (no crea rama, run, PR ni modifica
ROADMAP.md) — ver "Contexto de producto y bootstrap" en `AGENTS.md`.

## Propósito

Módulo COMMON, independiente, multitenant y reutilizable por N verticales
del Sistema Integral GI (Dental, Law, GI-OT, futuras). Primer producto:
gestión de Leads y su ciclo de vida comercial (captación, seguimiento,
asignación, conversión). No es una interfaz gráfica ni un CRM empresarial
completo en esta versión — el alcance es la capacidad de negocio de Leads.

## Límites de responsabilidad (arquitectura GI)

- **gi-platform-core**: organizaciones, sedes, identidad de acceso, usuarios,
  membresías, autenticación, autorización, multitenancy. CRM consume su
  superficie pública, nunca la duplica.
- **gi-common-persons**: personas físicas, identificadores, contacto,
  vínculo organizacional, resolución/deduplicación de personas. Fuente
  autorizada de datos generales de personas; CRM no implementa un sistema
  paralelo.
- **gi-common-crm** (este repo): Leads, origen/canal de captación, ciclo de
  vida comercial, asignación de responsables, actividades y seguimiento,
  historial comercial, conversión y cierre comercial.
- **Verticales** (Dental, Law, GI-OT, ...): sólo sus especializaciones
  propias (p.ej. Patient en Dental). Consumen los contratos públicos de
  Core/Persons/CRM; no duplican sus capacidades.

Principio obligatorio: lo reutilizable pertenece a COMMON, lo específico de
cada negocio pertenece a la vertical. Core y Persons nunca dependen de CRM;
CRM nunca depende de una vertical. Sin dependencias circulares ni claves
foráneas físicas entre bases de datos de servicios separados.

## Persona vs. Lead vs. entidad de vertical

Person (Persons) es la persona física. Lead (CRM) es un proceso comercial
con ciclo de vida propio, que puede existir sin Person identificada todavía
(captación incompleta) y luego vincularse a una Person existente o nueva.
Una Person puede tener N Leads en el tiempo y en distintas
organizaciones/verticales — `person_id` en Lead es opcional y sin `UNIQUE`.
Cliente/Paciente/Profesional/oportunidad futura son conceptos de la
vertical, no de CRM ni de Persons; CRM sólo conserva una referencia lógica
(`LeadExternalReference`) hacia la entidad que la vertical cree al
convertir el Lead.

## Integración Core y Persons (estado real verificado, no supuesto)

- `gi-platform-core` `v0.1.0` (release publicado) expone **sólo biblioteca
  Python** (`CoreApi.authorize` y superficie relacionada); **no hay HTTP
  desplegado**. Bloqueo real para la Modalidad B (HTTP) con Core.
- `gi-common-persons` (fundación + milestone 02-07 mergeados a `develop`,
  sin release/tag todavía) expone **sólo biblioteca Python**
  (`PersonsApi.find_duplicate_candidates`, `get_person`, `create_person`,
  etc.); **no hay HTTP desplegado** tampoco.
- CRM debe poder operar hoy en Modalidad A (biblioteca) mediante puertos
  locales (`Protocol`) que un `CoreApi`/`PersonsApi` real ya satisface por
  forma. La Modalidad B (HTTP) se deja preparada contra un contrato
  documentado, marcada explícitamente como no verificable end-to-end hasta
  que Core/Persons publiquen un servicio HTTP real.

## Reglas de negocio conocidas

- Aislamiento multitenant estricto: ninguna operación de Lead, actividad,
  historial, búsqueda de duplicados o conversión puede filtrar información
  entre organizaciones, incluso si Persons/Core no están disponibles
  (fail-safe: no se autoriza por defecto ante caída de una dependencia).
- Cardinalidad: Organization 1—N Lead; Person 0..1—N Lead (sin UNIQUE);
  Lead 1—N actividad/evento de estado/evento de asignación; Lead 0..N
  `LeadExternalReference` (una por vertical/tipo/id externo, `UNIQUE` en
  esa terna) para representar conversión sin acoplar CRM a la vertical.
- No se incorporan campañas, oportunidades avanzadas ni marketing
  automatizado en esta versión — fuera de alcance explícito del GOAL.

## Persistencia y convenciones ya adoptadas por el ecosistema (verificadas)

PostgreSQL vía Supabase, sin ORM/Alembic: SQL versionado en
`supabase/migrations/`, esquema propio por servicio (`persons.*` en
Persons), PK compuesta `(organization_id, id)`, RLS por
`current_setting('app.organization_id', true)`, adaptador DB-API 2.0 puro
que no importa el driver. CRM sigue la misma convención (`crm.*`) para
consistencia entre servicios COMMON del Sistema Integral GI. El proyecto
Supabase compartido (`gletzbwuvmwjkmoufmyj`, usado hoy por Core y Persons)
es infraestructura ajena en uso: aplicar migraciones ahí es una decisión
tardía y explícita, no parte de la base ni de las pruebas automáticas
(que corren contra Postgres efímero local/CI).

## Restricciones funcionales

- No inventar reglas de negocio, permisos, catálogos de país/documento,
  retención o contenido legal no provisto por el GOAL o por decisión humana
  explícita.
- No declarar disponible una integración HTTP con Core o Persons mientras
  no exista un servicio real desplegado — se documenta como bloqueo.
- No aplicar migraciones ni mutar el proyecto Supabase compartido sin
  autorización humana explícita previa (es infraestructura de otros
  productos reales en uso).
- No fusionar PR ni publicar el release `v0.1.0` sin decisión humana
  (único HITL del circuito, más la decisión de versión/tag).

## Decisiones de producto ya adoptadas

- Alcance v0.1.0: Leads (alta, consulta, filtro/paginación, edición,
  transición de estado validada, asignación/reasignación, actividades,
  historial, detección de duplicados vía Persons, vínculo con Person,
  cierre/descarte, conversión comercial con referencia externa a la
  vertical). Sin UI gráfica.
- Paquete `gi_crm` sin dependencias de runtime obligatorias (igual que
  `gi_platform_core`/`gi_persons`); FastAPI/psycopg como *extras*
  opcionales para las modalidades HTTP/Postgres.
- Cardinalidad Person↔Lead no única (ver arriba); confirmado por el GOAL,
  no requiere confirmación humana adicional.

## Límites generales

Fuera de alcance de este documento y de v0.1.0: UI gráfica, campañas y
marketing automatizado, oportunidades avanzadas más allá del Lead,
despliegue a la infraestructura Supabase compartida (unidad tardía y
condicionada a autorización humana), integración HTTP real con Core/Persons
(bloqueada hasta que existan del lado de esos repos).
