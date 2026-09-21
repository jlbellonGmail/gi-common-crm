# Spec: Milestone leads-core-implementation (ítems 02–06)

## Objetivo

Implementar la primera versión funcional (v0.1.0) del dominio de Leads de
GI-COMMON-CRM: contratos de integración con Core/Persons, dominio con
máquina de estados y detección de duplicados, persistencia aislada por
organización sobre PostgreSQL, API pública de biblioteca y HTTP, y
seguimiento multivertical (actividades, asignación, conversión) — probado
real, documentado e integrable por las verticales del Sistema Integral GI,
sin acoplar CRM a ninguna vertical concreta.

Este spec no vuelve a derivar decisiones de arquitectura ya fijadas y
aprobadas en la unidad `01-fundacion-diseno`: parte de
[arquitectura-crm.md](../../docs/tecnica/arquitectura-crm.md) (ADR-C01 a
ADR-C06, ya mergeados a `develop`) y de la descomposición/matriz de pruebas
de [plan-crm.md](../../docs/tecnica/plan-crm.md). Reafirma esas decisiones
como vinculantes para esta unidad y las traduce en criterios de aceptación
verificables.

## Contexto

`01-fundacion-diseno` está cerrada (`[x]` en `ROADMAP.md`, PR #1 mergeada a
`develop`). Los contratos reales de `gi-platform-core` (`CoreApi.authorize`,
release `v0.1.0`) y `gi-common-persons` (`PersonsApi`, milestone 02-07 en
`develop`, sin release propio todavía) fueron verificados directamente en
código, no asumidos — ver "Estado ya verificado" del plan original y
`arquitectura-crm.md`. Ninguno de los dos expone HTTP desplegado hoy; ambos
son sólo biblioteca Python con cero dependencias de runtime.

No existe todavía implementación de producto (`gi_crm`) ni `tests_crm/`: es
exactamente el alcance de este Milestone. `product-tests` en
`.github/workflows/ci.yml` sigue siendo el placeholder heredado del
template hasta que este Milestone lo sustituya por ejecución real.

## Alcance

Incluye, por ítem (dependencias según `plan-crm.md`):

- **02-contratos-integracion**: `Protocol` locales `CoreApi`/`PersonsApi` en
  `gi_crm.ports` (sin importar `gi_platform_core`/`gi_persons`), fakes de
  test para ambos, adaptadores HTTP (`adapters/core_http.py`,
  `adapters/persons_http.py`) documentados y marcados explícitamente
  bloqueados/no verificables end-to-end.
- **03-dominio-leads**: modelos (`Lead`, `LeadSource`, `LeadStatusEvent`,
  `LeadActivity`, `LeadAssignmentEvent`, `LeadExternalReference`,
  `LeadAudit`), `LeadService` con máquina de estados
  (`new→contacted→qualified→in_progress→(won|lost)`, `archived`),
  detección de duplicados vía `PersonsApi.find_duplicate_candidates`,
  concurrencia optimista (`version`/`expected_version`), todo probado con
  `InMemoryLeadStore`.
- **04-persistencia-aislamiento**: esquema SQL `crm.*` en
  `supabase/migrations/`, PK compuesta `(organization_id, id)`, RLS por
  `current_setting('app.organization_id', true)`, triggers `updated_at` y
  auditoría append-only, `PostgresLeadStore` DB-API 2.0 puro; pruebas reales
  contra Postgres efímero (Docker local / servicio en CI).
- **05-api-publica**: `LeadsApi` de biblioteca (paginación por cursor
  firmado, errores JSON-safe) y API HTTP FastAPI con OpenAPI; equivalencia
  funcional demostrada entre ambas modalidades.
- **06-seguimiento-multivertical**: actividades, asignación/reasignación con
  historial, consulta de historial comercial, `add_external_reference`/
  `convert_lead` para verticales, sin que `gi_crm` importe ni referencie por
  nombre ninguna vertical concreta.

También incluye pruebas reales contra PostgreSQL efímero (Docker local,
`@pytest.mark.integration` activada por `CRM_TEST_DATABASE_URL`, mismo
patrón que `PERSONS_TEST_DATABASE_URL` en `gi-common-persons`) y la
documentación técnica/de usuario de cada ítem del manifest
(`docs/tecnica/<docSlug>.md`/`docs/usuario/<docSlug>.md` para
`02-contratos-integracion`, `03-dominio-leads`,
`04-persistencia-aislamiento`, `05-api-publica`,
`06-seguimiento-multivertical` — el nombre real lo deriva
`Get-WorkUnitInfo -Mode Feature` por ítem, no un nombre libre por tema).

**Fuera de alcance** (explícitamente, por decisión ya registrada):

- Desplegar o tocar el proyecto Supabase compartido
  (`gletzbwuvmwjkmoufmyj`) usado hoy por Core/Persons — es la unidad
  `08-persistencia-supabase-real`, diferida y condicionada a autorización
  humana previa.
- Verificar la integración HTTP con Core/Persons end-to-end contra un
  servicio real — ninguno de los dos lo expone hoy; se documenta como
  bloqueado, no se simula como probado.
- UI gráfica, campañas/marketing automatizado, oportunidades avanzadas más
  allá del Lead, acoplar `gi_crm` a cualquier vertical concreta (Dental,
  Law, GI-OT).
- **Sustituir el placeholder `product-tests` de `.github/workflows/ci.yml`
  por un job de CI real con Postgres de servicio**: pertenece
  explícitamente a `07-readiness-integracion` según `ROADMAP.md` ("CI real
  (product-tests deja de ser placeholder)"), no a este Milestone —
  corrección de alcance respecto a una frase de `plan-crm.md` que sugería
  lo contrario; ver "Contradicción resuelta" en `decision.md`. Mismo
  patrón que siguió `gi-common-persons`: su propio milestone 02-07
  implementó dominio y persistencia con pruebas reales de Postgres
  opcionales (`PERSONS_TEST_DATABASE_URL`) y dejó el placeholder de
  `product-tests` intacto hasta su unidad `07-readiness-integracion`.
- `07-readiness-integracion` (documentación de release/supply-chain
  completa, CI real) y el tag/release `v0.1.0` — unidades y decisión
  posteriores, separadas de este Milestone.

## Criterios de aceptación

Se listan como comprobables por prueba automatizada, en línea con la
"Matriz mínima de pruebas" de `plan-crm.md`:

1. **Límites de módulos**: `gi_crm` no importa `gi_platform_core` ni
   `gi_persons`; sólo usa los `Protocol` locales de `gi_crm.ports`. Ninguna
   vertical es importada ni referenciada por nombre.
2. **Aislamiento multitenant**: una organización A no puede leer, listar,
   modificar, asignar, agregar actividad, vincular Person ni convertir un
   Lead de la organización B; la búsqueda de duplicados no filtra
   candidatos de otra organización. Probado negativamente, no sólo por
   inspección del esquema.
3. **Autorización fail-safe**: sin el permiso `crm:lead:<acción>` la
   operación se deniega; si `CoreApi` no está disponible, nunca se autoriza
   por defecto (`CoreUnavailableError`); el permiso de sede (`location_id`)
   se respeta cuando aplica.
4. **Persons caído**: `link_person` y la detección de duplicados fallan
   explícitamente (`PersonsUnavailableError`) sin bloquear el resto del
   ciclo de vida del Lead.
5. **Cardinalidad Person↔Lead**: una misma Person puede tener N Leads en el
   tiempo y en distintas organizaciones sin colisión; ausencia de `UNIQUE`
   sobre `person_id` verificada por test.
6. **Máquina de estados**: transición inválida rechazada
   (`InvalidTransitionError`); cada transición válida genera un
   `LeadStatusEvent` append-only; `archived` alcanzable desde cualquier
   estado no terminal.
7. **Concurrencia optimista**: dos actualizaciones concurrentes con la
   misma `version` de origen — una gana, la otra recibe
   `VersionConflictError`; el evento perdedor de una asignación concurrente
   no se pierde del historial.
8. **Conversión/vertical**: `add_external_reference` respeta
   `UNIQUE(organization_id, vertical_code, external_type, external_id)`; un
   segundo intento con la misma terna se rechaza explícitamente, no se
   ignora ni duplica silenciosamente.
9. **Persistencia real**: pruebas contra Postgres efímero (no sólo
   `InMemoryLeadStore`); RLS activo sin bypass posible desde el adaptador;
   la migración es aplicable e idempotente sobre una base nueva.
10. **Equivalencia de contrato**: `LeadsApi` (biblioteca) y la API HTTP dan
    la misma respuesta funcional para la misma operación; errores
    JSON-safe sin fuga de detalles internos; paginación por cursor estable
    entre páginas.
11. **Modalidad HTTP con Core/Persons**: los adaptadores sólo se prueban
    contra un servidor HTTP simulado; ningún test ni documento declara esta
    integración como verificada end-to-end.
12. **Pruebas reales de persistencia disponibles, sin exigir CI todavía**:
    `pytest -q tests_crm/` corre íntegro en verde con
    `InMemoryLeadStore`/fakes sin ninguna dependencia externa; el
    subconjunto marcado `@pytest.mark.integration` contra
    `PostgresLeadStore` se activa y pasa localmente con
    `CRM_TEST_DATABASE_URL` apuntando a un Postgres efímero (Docker), con
    evidencia real en `test-report-1.md`. `circuit-tests`
    (`pytest -q tests/`) sigue en verde sin regresiones. El placeholder
    `product-tests` de `.github/workflows/ci.yml` permanece sin tocar en
    esta unidad (alcance de `07-readiness-integracion`).

## Supuestos y clarificaciones ya resueltas

Registradas en `plan-crm.md` ("Clarificaciones materiales pendientes") y
reafirmadas aquí como no bloqueantes para iniciar la implementación:

- Catálogo inicial de `LeadSource`: `website`, `referral`, `phone`,
  `walk_in`, `other`, modelado como datos de catálogo por organización (no
  tipo enumerado de base), ampliable sin migración de esquema.
- Motivos de cierre (`won`/`lost`) siguen el mismo criterio de catálogo
  extensible, no lista cerrada en código.
- Nombres de permisos `crm:lead:*` se definen en el ítem
  `02-contratos-integracion`, siguiendo el patrón ya usado por Persons para
  registrar sus propios permisos en Core — sin inventar un esquema de
  permisos distinto al de Core.
- Compatibilidad de CRM se fija contra el commit de `develop` de Persons
  vigente al iniciar este Milestone (sin release propio de Persons
  todavía); riesgo de fundación movediza si Persons publica cambios
  incompatibles antes de que CRM alcance su propio release — se registra,
  no se bloquea por ello.

No hay una CLARIFY abierta que impida iniciar la implementación: toda
ambigüedad material identificada hasta ahora ya tiene una resolución
explícita registrada en `plan-crm.md`/`arquitectura-crm.md`.

## Riesgos

- Persons sin release propio (riesgo de fundación movediza, ya registrado).
- Adaptadores HTTP de Core/Persons no verificables end-to-end hasta que
  esos repos publiquen un servicio real — riesgo aceptado y documentado,
  no oculto.
- Alcance grande para una sola PR de Milestone (5 ítems interdependientes):
  mitigado dividiendo la implementación en commits por ítem dentro de la
  misma rama, con evidencia y checklist de `tasks.md` por ítem, aunque el
  cierre de `ROADMAP.md` sea atómico para los 5 al mergear.
