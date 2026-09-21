# Ítem 03 — Dominio de Leads

## Para qué sirve

Es el corazón de CRM: un Lead nace, avanza por un ciclo comercial
(`new → contacted → qualified → in_progress → won/lost`, o se archiva en
cualquier momento) y puede vincularse a una Person ya existente o quedar
sin identificar hasta que se sepa quién es.

## Cómo usarlo

```python
from gi_crm.memory import InMemoryLeadStore
from gi_crm.service import LeadService

service = LeadService(InMemoryLeadStore(), core_api, persons_api)
lead = service.create_lead(context, title="Consulta desde el sitio web")
lead = service.change_status(context, lead.lead_id, lead.version, "contacted")
```

Cada cambio de estado exige la `version` actual del Lead (evita que dos
personas pisen el mismo cambio sin saberlo) y queda registrado en el
historial — nunca se pierde quién cambió qué y cuándo.

## Cómo verificarlo

`pytest -q tests_crm/test_service_domain.py
tests_crm/test_service_concurrency.py tests_crm/test_service_duplicates.py
tests_crm/test_tenant_isolation.py tests_crm/test_cardinality.py` — cubren
transiciones válidas e inválidas, conflictos de versión, duplicados vía
Persons y que una organización nunca ve los Leads de otra.
