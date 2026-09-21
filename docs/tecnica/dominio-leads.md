# Ítem 03 — Dominio de Leads (`LeadService`)

Ver [Arquitectura de CRM](arquitectura-crm.md) (ADR-C01, ADR-C06) para el
razonamiento de diseño. Este documento describe la implementación real en
`gi_crm/service.py`, `gi_crm/models.py` y `gi_crm/memory.py`.

## Modelo de datos

`Lead` (`lead_id`, `organization_id`, `status`, `person_id` opcional sin
`UNIQUE`, `source_id`, `owner_user_id`, `title`, `description`,
`close_reason`, `version`, `created_at`, `updated_at`), más las entidades
append-only `LeadStatusEvent`, `LeadActivity`, `LeadAssignmentEvent`,
`LeadExternalReference` y `LeadAudit`. Todas son dataclasses `frozen,
slots`. `json_value()` normaliza `UUID`/`datetime` para cualquier fachada
JSON-safe (ver [ítem 05](api-publica.md)).

## Máquina de estados comercial

```
new → contacted → qualified → in_progress → (won | lost)
```

`archived` es alcanzable desde cualquier estado no terminal. `won`,
`lost` y `archived` son terminales (`TERMINAL_STATUSES`, sin transición
saliente). `VALID_TRANSITIONS` en `gi_crm/models.py` es la única fuente
de verdad; `LeadService.change_status` valida contra el estado **real**
del Lead (no contra la vista del llamador) y rechaza con
`InvalidTransitionError` cualquier salto no permitido. `close_lead`
delega en `change_status` exigiendo `outcome in ("won", "lost")`.

Cada transición registra un `LeadStatusEvent` append-only con el estado de
origen, destino, actor y motivo opcional — el historial nunca se
sobrescribe (`list_status_history`).

## Concurrencia optimista

Toda escritura (`update_lead`, `change_status`, `assign_lead`) exige
`expected_version`; el store (`InMemoryLeadStore.update_lead`) compara
contra la versión real y lanza `VersionConflictError` si no coincide,
igual criterio que `gi_persons.Person`. Verificado en
`tests_crm/test_service_concurrency.py`.

## Detección de duplicados y vínculo con Person

`find_duplicate_candidates` y `link_person` delegan en `PersonsApi`
(puerto, sin importar `gi_persons`). Si `persons_api` es `None` o la
llamada falla, la operación levanta `PersonsUnavailableError` — nunca
falla en silencio ni bloquea el resto del ciclo de vida del Lead
(`tests_crm/test_service_duplicates.py`). `person_id` es opcional y sin
unicidad: una misma Person puede tener N Leads (ADR-C01, verificado en
`tests_crm/test_cardinality.py`).

## Aislamiento multitenant

Toda operación filtra por `organization_id` en el store, no sólo en el
service; una organización nunca ve ni afecta Leads, actividades,
historial, asignaciones o candidatos a duplicado de otra
(`tests_crm/test_tenant_isolation.py`, pruebas negativas explícitas).
