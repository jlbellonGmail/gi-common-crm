# Ítem 05 — API pública (`LeadsApi` y HTTP)

Ver [Arquitectura de CRM](arquitectura-crm.md) (ADR-C02, ADR-C05) para el
razonamiento de por qué la lógica vive sólo en `service.py`. Este
documento describe la fachada real.

## `LeadsApi` (`gi_crm/api.py`) — modalidad biblioteca

Fachada JSON-safe sobre `LeadService`: cada método recibe/devuelve tipos
primitivos (`str`, no `UUID`; ISO 8601, no `datetime`), vía `json_value()`.
`error(exc)` mapea cualquier `CrmError` a `{"code", "message"}` y cualquier
excepción no reconocida a `{"code": "INTERNAL_ERROR", ...}` — sin fuga de
detalles internos.

### Paginación por cursor

`CursorCodec` firma con HMAC-SHA256 un payload
`{"o": organization_id, "f": filters, "l": last_id}`, codificado en
base64url. `list_leads(limit, cursor)` pide `limit + 1` al service para
saber si hay más páginas sin una segunda consulta `COUNT`. Un cursor
alterado (payload o firma) siempre lanza `ValidationError` — nunca se
decodifica un cursor no confiable. Verificado en
`tests_crm/test_api_library.py` (paginación estable entre páginas,
rechazo de cursor manipulado).

## API HTTP (`gi_crm/http/`) — extra opcional `[http]`

`gi_crm/http/` no se importa nunca desde `gi_crm/__init__.py` ni desde
ningún módulo base: instalar sólo la biblioteca (`pip install
gi-common-crm`) no arrastra FastAPI/Pydantic. `create_app(leads_api)`
monta el contexto de tenant desde cabeceras confiables (`X-GI-User-Id`,
`X-GI-Organization-Id`, `X-GI-Location-Id`, ADR-C03/ADR-C05) — ausentes o
inválidas, la petición responde `400` (no el `422` genérico de Pydantic,
para no exponer dos contratos de error distintos). Un único
`@app.exception_handler(CrmError)` traduce cada error de dominio a su
código HTTP (`gi_crm/http/errors.py::status_for`): `400` validación,
`403` prohibido, `404` no encontrado, `409` conflicto de versión/
transición inválida/referencia duplicada, `503` Core o Persons
indisponibles, `501` capacidad no disponible, `500` genérico.

Cada endpoint (`POST/GET /v1/leads`, `GET/PATCH /v1/leads/{id}`,
`POST /v1/leads/{id}/status`, `/close`, `/assign`, `/activities`,
`/link-person`, `/external-references`, `/convert`, y sus `GET` de
listado/historial) delega **íntegramente** en `LeadsApi` — no reimplementa
ninguna regla. `tests_crm/test_http_contract.py` verifica que biblioteca y
HTTP responden lo mismo ante la misma operación, y que `/openapi.json` es
alcanzable.
