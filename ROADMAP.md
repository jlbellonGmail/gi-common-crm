# ROADMAP

Plan de fundación e implementación de GI-COMMON-CRM (Leads). Sin versión de
release decidida. Todas las unidades siguen pendientes hasta atravesar el
circuito real (branch propia, PR, CI verde, HITL de merge). El expediente de
bootstrap no cierra ninguna por sí mismo.

## Backlog

- [x] 01-fundacion-diseno — consolidar decisiones, procedencia, contratos reales de Core/Persons y arquitectura del dominio CRM; adoptar el circuito.
- [x] 02-contratos-integracion — puertos locales `CoreApi`/`PersonsApi`, adaptadores de biblioteca y de HTTP (HTTP documentado y marcado bloqueado hasta que Core/Persons lo desplieguen), fakes de prueba.
- [x] 03-dominio-leads — modelos de dominio, `LeadService`, máquina de estados comerciales validada, detección de duplicados, concurrencia optimista.
- [x] 04-persistencia-aislamiento — esquema SQL `crm.*`, RLS por organización, `PostgresLeadStore`, `InMemoryLeadStore`, pruebas reales contra PostgreSQL efímero.
- [x] 05-api-publica — `LeadsApi` de biblioteca (paginación por cursor, errores JSON-safe) y API HTTP versionada con OpenAPI.
- [x] 06-seguimiento-multivertical — actividades, asignación/reasignación, historial comercial y referencias de conversión para verticales, sin acoplar CRM a ninguna.
- [x] 07-readiness-integracion — CI real (product-tests deja de ser placeholder), documentación completa, supply-chain, evidencia para HITL de release.
- [x] 08-persistencia-supabase-real — desplegar y verificar la migración `crm.*` en el proyecto Supabase real compartido con Core/Persons. Requiere autorización humana explícita antes de iniciarse, no sólo en el merge: toca infraestructura ajena en uso.
- [ ] 09-maintenance-release-readiness-project-scope — corregir el gate de release para que evalúe el alcance y la evidencia reales del proyecto, sin exigir unidades transversales del Template que no pertenecen al backlog CRM.

02 a 06 se ejecutan como un único Milestone (`leads-core-implementation`)
por su interdependencia directa, igual que hizo GI-COMMON-PERSONS con sus
unidades 02–07. 01, 07 y 08 son Features independientes.

Referencias y aceptación: [plan técnico](docs/tecnica/plan-crm.md) (se
agrega junto con la unidad 01). `[ ]` pendiente; `[-]` sólo `READY_FOR_PR`
real; `[x]` sólo después del merge confirmado a `develop`. No se decide un
tag ni una release en este documento.

## Fuentes de orientación

- [CONSTITUTION](CONSTITUTION.md) — principios permanentes.
- [AGENTS](AGENTS.md) — operación del circuito.
- [STATUS](STATUS.md) — estado actual para reentrada.
- [Contexto de producto](docs/producto/contexto-producto.md) — conocimiento funcional persistente.








