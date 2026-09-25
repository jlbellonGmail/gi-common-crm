"""Adaptador HTTP documentado de CoreApi.

BLOQUEADO / no verificable end-to-end: reverificado contra `gi-platform-core`
`v0.2.1` (tag real, no supuesto). `authorize()` como método de biblioteca
Python (`CoreApi.authorize` en `contracts.py`) no cambió su forma desde
`v0.1.0` -- compatible con este adaptador sin ajustes. `v0.2.1` sí agregó un
adaptador HTTP propio (`gi_platform_core/http.py`), pero expone únicamente
`/v1/organizations/{id}/identity-validation` e `/identity-links`; **no
expone ninguna ruta de autorización** (`/v1/authorize` no existe en Core).
Esta integración HTTP sigue bloqueada/no verificable end-to-end por esa
razón, no por ausencia total de servicio HTTP en Core como asumía la
verificación anterior (ver docs/tecnica/contratos-integracion.md). Este
adaptador implementa el `Protocol CoreApi` de gi_crm.ports contra el *shape*
JSON documentado de `CoreApi.authorize`, y sólo se prueba en
tests_crm/test_adapters_http.py contra un transporte simulado -- ningún
test de este repositorio declara esta integración como probada contra un
servicio real.
"""


class CoreHttpApi:
    """Implementa gi_crm.ports.CoreApi vía HTTP.

    `transport` es inyectado por el host: `callable(method, url, *,
    json=None) -> dict`. No se importa ningún cliente HTTP concreto aquí
    para no forzar una dependencia de runtime a quien sólo use la
    biblioteca en proceso.
    """

    def __init__(self, base_url: str, transport):
        self.base_url = base_url.rstrip("/")
        self.transport = transport

    def authorize(self, user_id: str, tenant_id: str, permission: str, location_id: str | None = None) -> dict:
        payload = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "permission": permission,
            "location_id": location_id,
        }
        return self.transport("POST", f"{self.base_url}/v1/authorize", json=payload)
