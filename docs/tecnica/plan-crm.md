# Plan de unidades de trabajo

Diseño inicial primero. El bootstrap local no sustituye identidad de work
unit, ASSESS, review, PR ni HITL. Ninguna unidad se marca completada por
redactarla; sólo el merge confirmado a `develop` cierra un ítem del
[ROADMAP](../../ROADMAP.md).

## Adopción del Template

Baseline: `template-starter` tag/circuito v2.0.1, snapshot del commit
`bfd363f` ("docs: remove final broken starter link"). Se copió el circuito
y los tests como snapshot (`git init` propio, sin historia/tags/releases ni
evidencia de Template), se adaptó identidad del proyecto
(`gi-common-crm`) y se conservó procedencia en el commit inicial. No se
tocó `C:\Proyectos\template` (repositorio histórico, explícitamente
excluido por el GOAL) en ningún momento.

Repositorio remoto ya identificado (`jlbellonGmail/gi-common-crm`, vacío al
inicio): `main` y `develop` se crearon y publicaron directamente durante el
bootstrap. Corrección aplicada en esta misma unidad: crear `main` antes de
una release real contradice la "Decisión: ciclo de vida de `main`" heredada
del circuito (ver [arquitectura.md](arquitectura.md)); se eliminó `main`
local y remota y se fijó `develop` como rama por defecto del repositorio.
GI-COMMON-CRM queda sin rama `main` hasta que exista una decisión humana
real de release, igual que el resto del ecosistema GI.

## Descomposición y aceptación

| Unidad | Dependencias | Alcance y aceptación comprobable |
|---|---|---|
| U01 / 01-fundacion-diseno | remoto y circuito ya bootstrapeados; contratos reales de Core/Persons verificados (no supuestos) | Arquitectura (`arquitectura.md` + `arquitectura-crm.md`), modelo de dominio, contratos propuestos, límites de responsabilidad COMMON/vertical, corrección del ciclo de vida de `main`, circuito de tests del template en verde (267 passed) |
| Milestone `leads-core-implementation` (U02–U06) | U01 | Ver desglose de ítems abajo; una sola PR por interdependencia directa, igual criterio que Persons con su milestone 02-07 |
| 02-contratos-integracion | U01 | `Protocol` locales `CoreApi`/`PersonsApi` en `gi_crm.ports`; ningún import de `gi_platform_core`/`gi_persons`; fakes de test para ambos; adaptadores HTTP documentados y marcados explícitamente bloqueados/no verificables end-to-end (Core y Persons no exponen HTTP hoy) |
| 03-dominio-leads | 02 | `Lead`, `LeadSource`, `LeadStatusEvent`, `LeadActivity`, `LeadAssignmentEvent`, `LeadExternalReference`; `LeadService` con máquina de estados validada (`new→contacted→qualified→in_progress→(won\|lost)`, `archived`); detección de duplicados vía `PersonsApi.find_duplicate_candidates`; concurrencia optimista (`version`/`expected_version`); todo probado con `InMemoryLeadStore` |
| 04-persistencia-aislamiento | 03 | Esquema SQL `crm.*` en `supabase/migrations/`, PK compuesta `(organization_id, id)`, RLS por `current_setting('app.organization_id', true)`, triggers `updated_at` y auditoría append-only, `PostgresLeadStore` DB-API 2.0 puro; pruebas reales contra Postgres efímero (Docker local / servicio en CI), nunca contra el Supabase compartido de Core/Persons |
| 05-api-publica | 03, 04 | `LeadsApi` de biblioteca (paginación por cursor firmado, errores JSON-safe) y API HTTP FastAPI con OpenAPI; equivalencia funcional demostrada entre ambas modalidades con la misma batería de tests de contrato |
| 06-seguimiento-multivertical | 03, 05 | Actividades, asignación/reasignación con historial, consulta de historial comercial, `add_external_reference`/`convert_lead` para verticales, sin que CRM importe ni conozca ninguna vertical concreta |
| U07 / 07-readiness-integracion | Milestone 02-06 mergeado | `product-tests` deja de ser placeholder (Postgres real de servicio en CI), documentación completa (API pública, modelo de datos, guía de integración multivertical), supply-chain e integridad verificadas, evidencia lista para HITL de release |
| U08 / 08-persistencia-supabase-real | U07; **autorización humana explícita previa a iniciarse** | Migración `crm.*` desplegada y verificada en el proyecto Supabase compartido (`gletzbwuvmwjkmoufmyj`) usado hoy por Core y Persons. No se inicia autónomamente: toca infraestructura ajena en uso |

El Milestone agrupa 02–06 por su interdependencia directa (el dominio, la
persistencia y la API pública de Leads no son revisables ni desplegables por
separado sin dejar contratos a medias), igual que hizo GI-COMMON-PERSONS con
su milestone 02-07. U01, U07 y U08 son Features independientes con su propia
PR. U08 no se agrupa: depende de una decisión humana que puede no llegar
dentro del alcance de este GOAL, y no debe bloquear el resto.

## Matriz mínima de pruebas

| Requisito | Casos de prueba antes de habilitarlo |
|---|---|
| Límites de módulos | `gi_crm` no importa `gi_platform_core`/`gi_persons`; sólo los `Protocol` locales; ninguna vertical importada ni referenciada por nombre |
| Tenant | Organización A no puede leer/listar/modificar/asignar/agregar actividad/vincular Person/convertir Lead de la organización B; búsqueda de duplicados no filtra candidatos de otra organización; contexto de organización nunca se toma de un parámetro sin verificar |
| Autorización | Sin permiso `crm:lead:<acción>` se deniega; Core caído nunca autoriza por defecto (`CoreUnavailableError`); permiso de sede (`location_id`) respetado cuando aplica |
| Persons caído | `link_person`/detección de duplicados fallan explícitamente (`PersonsUnavailableError`); el resto del ciclo de vida del Lead sigue operable |
| Cardinalidad | Una misma Person con N Leads en el tiempo y en distintas organizaciones no colisiona; ausencia de `UNIQUE` sobre `person_id` verificada por test, no sólo por lectura del esquema |
| Estados | Transición inválida rechazada (`InvalidTransitionError`); cada transición válida genera `LeadStatusEvent` append-only; `archived` alcanzable desde cualquier estado no terminal |
| Concurrencia | Dos actualizaciones con la misma `version` de origen: una gana, la otra recibe `VersionConflictError`; asignación concurrente no pierde el evento perdedor del historial |
| Conversión/vertical | `add_external_reference` respeta `UNIQUE(organization_id, vertical_code, external_type, external_id)`; segundo intento con la misma terna es rechazado, no silenciosamente ignorado ni duplicado |
| Persistencia | Pruebas reales contra Postgres efímero (no sólo `InMemoryLeadStore`); RLS activo sin bypass; migración aplicable e idempotente en una base nueva |
| Contrato | `LeadsApi` y la API HTTP dan la misma respuesta funcional para la misma operación; errores JSON-safe sin fuga de detalles internos; paginación por cursor estable entre páginas |
| Modalidad HTTP con Core/Persons | Adaptadores probados sólo contra servidor simulado; ningún test declara esta integración como verificada end-to-end mientras no exista un servicio real desplegado |

## SDD, QA, CI y HITL

1. Ejecutar `scripts/assess-work-unit.ps1` con las rutas reales del diff de
   cada unidad y conservar el JSONL de evidencia; `materialize-sdd.ps1`
   deriva LIGHT/STANDARD/FULL. No clasificar a mano.
2. Producir intención/plan (y `tasks.md` si la profundidad lo exige),
   separando hechos verificados de supuestos; no bloquear con CLARIFY
   decisiones ya resueltas explícitamente por el GOAL (cardinalidad
   Person↔Lead, alcance v0.1.0, exclusión de UI/campañas).
3. Implementar sólo el alcance habilitado por unidad. Ejecutar la suite del
   circuito (`tests/`) y la de producto (`tests_crm/`) antes de declarar
   cualquier paso hecho; evidencia real bajo `runs/<slug>/`.
4. Revisión del diff final contra el SHA vigente antes de pedir PR; un
   cambio posterior invalida una verificación previa — no se reutiliza un
   "aprobado" de otro estado del código.
5. Con gates locales aprobados, `ready-for-pr.ps1` → `[-]` READY_FOR_PR;
   publicar rama/PR contra `develop` y confirmar CI verde real (`gh pr
   checks`/`gh run list`), nunca inferido. No pedir HITL sobre CI en rojo
   ni sobre el placeholder `product-tests` sin sustituir.
6. Único HITL de merge: decisión humana MERGE/NO MERGE sobre PR real con CI
   verde. `complete-approved-pr.ps1` sólo tras esa decisión;
   `close-feature.ps1`/cierre de milestone confirma el merge y recién
   entonces el ítem pasa a `[x]` en `ROADMAP.md`. Tag/release `v0.1.0` es
   una decisión y ejecución humana separada, posterior a U07.

CI heredada exige `circuit-tests`, `product-tests` y
`local-reconciler-tests`. Mientras no exista implementación de producto
(unidad U01), `product-tests` sigue siendo el placeholder heredado del
template — igual que Core y Persons lo mantuvieron durante su propia
fundación. El Milestone 02-06 debe sustituirlo por una ejecución real de
`tests_crm/` con Postgres de servicio; no se declara cobertura de producto
antes de eso.

## Clarificaciones materiales pendientes

- Catálogo inicial de `LeadSource` (canales de captación) y de motivos de
  cierre/descarte: el GOAL no fija una lista cerrada; se define en
  U03 con valores mínimos razonables (`website`, `referral`, `phone`,
  `walk_in`, `other`) documentados como punto de partida, ampliable por
  organización sin migración de esquema si se modela como catálogo de
  datos y no de tipo enumerado en la base.
- Nombres exactos de permisos `crm:lead:*` a registrar en Core: se definen
  en U02 siguiendo el patrón ya usado por Persons para sus propios
  permisos (`contratos-persons.md`), sin inventar un esquema de permisos
  distinto al de Core.
- Persons no tiene release/tag todavía (sólo milestone 02-07 en
  `develop`): se fija el punto de compatibilidad de CRM contra ese commit
  concreto de `develop` de Persons hasta que exista un release propio, y se
  registra como riesgo de fundación movediza si Persons publica cambios
  incompatibles antes de que CRM alcance su propio release.

Estas cuestiones se resuelven en la unidad que dependa de ellas, sin frenar
la documentación y las pruebas ya independientes de U01. No se solicita
autorización para modificar Core ni Persons desde este GOAL: sólo se
registran impactos candidatos.
