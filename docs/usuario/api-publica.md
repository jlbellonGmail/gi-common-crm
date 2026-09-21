# Ítem 05 — API pública

## Para qué sirve

Permite usar CRM de dos formas equivalentes: como biblioteca Python dentro
de otro proceso (`gi_crm.api.LeadsApi`), o como servicio HTTP propio
(`gi_crm.http.app.create_app`) para quien prefiera integrar por red. Ambas
dan la misma respuesta ante la misma operación porque comparten toda la
lógica de negocio.

## Cómo usarla como biblioteca

```python
from gi_crm.api import LeadsApi

api = LeadsApi(service, cursor_secret=b"un-secreto-real-de-produccion")
creado = api.create_lead(context, title="Nuevo interesado")
pagina = api.list_leads(context, limit=20)
```

## Cómo levantar la API HTTP (requiere `pip install gi-common-crm[http]`)

```python
from gi_crm.http.app import create_app

app = create_app(api)  # uvicorn app --host 0.0.0.0 --port 8000
```

Cada petición debe llevar las cabeceras `X-GI-User-Id` y
`X-GI-Organization-Id` (inyectadas por el proxy/host autenticado, no por
el cliente final) — sin ellas, la respuesta es `400`. La documentación
interactiva queda disponible en `/docs` y el contrato en `/openapi.json`.
