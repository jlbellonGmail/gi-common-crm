# Ítem 02 — Contratos e integración

## Para qué sirve

Define cómo GI-COMMON-CRM habla con el resto del ecosistema (Core para
autorización, Persons para personas) sin depender directamente de ningún
código de esos repositorios. Así CRM se puede probar, versionar y publicar
solo, y ningún cambio interno de Core o Persons rompe CRM mientras
respeten la misma forma de respuesta.

## Cómo verificarlo

- `pytest -q tests_crm/test_ports_contract.py` — los puertos calzan con
  las implementaciones reales por forma, sin importarlas.
- `pytest -q tests_crm/test_contract_and_migration.py` — ningún módulo de
  `gi_crm` importa `gi_platform_core`, `gi_persons` ni el nombre de una
  vertical.
- `pytest -q tests_crm/test_adapters_http.py` — los adaptadores HTTP
  documentados arman la petición correcta contra un transporte simulado
  (la integración real contra un servicio HTTP de Core/Persons sigue
  bloqueada porque ninguno de los dos expone HTTP hoy).

## Permisos que debe conceder Core

Cada acción sobre un Lead requiere un permiso `crm:lead:<acción>`
específico (ver el catálogo completo en
[docs/tecnica/contratos-integracion.md](../tecnica/contratos-integracion.md)).
Sin el permiso correspondiente, o si Core no responde, la operación se
rechaza — nunca se permite por defecto.
