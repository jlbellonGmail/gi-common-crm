"""Adaptador HTTP documentado de CoreApi.

BLOQUEADO / no verificable end-to-end: `gi-platform-core` (`v0.1.0`) sólo
expone biblioteca Python hoy, sin servicio HTTP desplegado (verificado en
código, ver docs/tecnica/contrato-core.md). Este adaptador implementa el
`Protocol CoreApi` de gi_crm.ports contra el *shape* JSON documentado de
`CoreApi.authorize`, y sólo se prueba en tests_crm/test_adapters_http.py
contra un transporte simulado -- ningún test de este repositorio declara
esta integración como probada contra un servicio real.
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

    def authorize(self, user_id: str, organization_id: str, permission: str, location_id: str | None = None) -> dict:
        payload = {
            "user_id": user_id,
            "organization_id": organization_id,
            "permission": permission,
            "location_id": location_id,
        }
        return self.transport("POST", f"{self.base_url}/v1/authorize", json=payload)
