# Ítem 02 — Contratos e integración (CoreApi/PersonsApi)

Ver [Arquitectura de CRM](arquitectura-crm.md) (ADR-C01, ADR-C02, ADR-C05)
para las decisiones que este ítem implementa. Este documento describe la
forma real de los puertos y el catálogo de permisos, no repite el ADR.

## Puertos locales (`gi_crm/ports.py`)

`gi_crm` no importa `gi_platform_core` ni `gi_persons` como dependencia
dura. Define sus propios `Protocol`:

- `CoreApi.authorize(user_id, organization_id, permission, location_id=None)
  -> dict` — mismo *shape* de respuesta que `gi_platform_core.CoreApi`:
  `{"contract_version", "allowed", "reason", "context"}`.
- `PersonsApi` (subconjunto usado por CRM): `find_duplicate_candidates`,
  `get_person`, `create_person`.
- `AuditSink.append(event: LeadAudit)`.
- `LeadStore`: puerto de persistencia (`create_lead`, `get_lead`,
  `list_leads`, `update_lead`, `append_status_event`, `list_status_events`,
  `append_activity`, `list_activities`, `append_assignment`,
  `list_assignments`, `add_external_reference`, `list_external_references`).

Una implementación real de `CoreApi`/`PersonsApi` calza por forma (duck
typing); no hace falta un adapter de código para la modalidad biblioteca.
`tests_crm/test_contract_and_migration.py` verifica estáticamente que
ningún módulo de `gi_crm` importa `gi_platform_core`, `gi_persons` ni el
nombre de ninguna vertical.

## Catálogo de permisos `crm:lead:*`

Cada operación de `LeadService` exige exactamente uno de estos permisos vía
`CoreApi.authorize`, antes de tocar el store (ADR-C03, fail-closed):

| Permiso | Operaciones |
| --- | --- |
| `crm:lead:write` | `create_lead`, `update_lead` |
| `crm:lead:read` | `get_lead`, `list_leads`, `list_status_history`, `list_assignments`, `list_external_references` |
| `crm:lead:status:write` | `change_status`, `close_lead` |
| `crm:lead:assign:write` | `assign_lead`, `reassign_lead` |
| `crm:lead:activity:write` | `add_activity` |
| `crm:lead:activity:read` | `list_activities` |
| `crm:lead:link:write` | `link_person`, `find_duplicate_candidates` |
| `crm:lead:external-reference:write` | `add_external_reference` |
| `crm:lead:convert:write` | `convert_lead` |

Este catálogo resuelve la clarificación ya registrada en
[plan-crm.md](plan-crm.md) sobre el nombrado de permisos `crm:lead:*`.

## Adaptadores HTTP documentados, bloqueados end-to-end (ADR-C05)

`gi_crm/adapters/core_http.py` (`CoreHttpApi`) y
`gi_crm/adapters/persons_http.py` (`PersonsHttpApi`) implementan los
puertos contra un contrato JSON documentado, recibiendo un `transport`
inyectado (`callable(method, url, *, json=None) -> dict`) para no forzar
ninguna dependencia de cliente HTTP concreta en `gi_crm`.
`tests_crm/test_adapters_http.py` sólo prueba estos adaptadores contra un
transporte simulado — la integración real sigue explícitamente bloqueada y
no se declara probada.

Reverificado contra `gi-platform-core v0.2.1` (tag real) y el `develop`
actual de `gi-common-persons`: `CoreApi.authorize` no cambió de forma
respecto de `v0.1.0` (compatible sin ajustes). Persons sigue sin exponer
ningún módulo HTTP en el código real. Core sí agregó un adaptador HTTP
propio en `v0.2.1` (`gi_platform_core/http.py`), pero cubre únicamente
`/v1/organizations/{id}/identity-validation` e `/identity-links`
(vinculación de identidad Core↔Persons); no existe ninguna ruta de
autorización (`/v1/authorize`). El bloqueo de `CoreHttpApi` se mantiene
por esa razón — falta de superficie HTTP para `authorize`, la única
capacidad de Core que CRM consume — no por ausencia total de servicio HTTP
en Core.

## Fakes de prueba

`tests_crm/fakes.py` define `FakeCoreApi` (permite/deniega/simula fallo
de transporte, respeta `contract_version`) y `FakePersonsApi` (duplicados,
`get_person`, `create_person`, simula fallo), usados por toda la batería
de dominio/aislamiento/autorización sin depender de Core o Persons reales.
