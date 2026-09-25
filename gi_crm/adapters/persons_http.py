"""Adaptador HTTP documentado del subset de PersonsApi usado por gi_crm.

BLOQUEADO / no verificable end-to-end: reverificado contra
`gi-common-persons` en `develop` (milestone 02-07 + identity-linking
mergeados, sin release/tag propio todavía). Las firmas reales de
`create_person`/`get_person`/`find_duplicate_candidates` en `gi_persons/
api.py` no cambiaron; compatibles con este adaptador sin ajustes. Persons
sigue sin exponer ningún módulo HTTP (ni WSGI ni ASGI) en el código real,
a diferencia de Core que sí agregó uno en `v0.2.1` (ver
gi_crm/adapters/core_http.py). Esta integración sigue bloqueada/no
verificable end-to-end (ver docs/tecnica/contratos-integracion.md). Sólo
se prueba en tests_crm/test_adapters_http.py contra un transporte
simulado.
"""


class PersonsHttpApi:
    """Implementa el subset de gi_crm.ports.PersonsApi vía HTTP.

    `transport` inyectado por el host, mismo criterio que `CoreHttpApi`.
    """

    def __init__(self, base_url: str, transport):
        self.base_url = base_url.rstrip("/")
        self.transport = transport

    def find_duplicate_candidates(self, context, *, keys, limit: int = 20) -> dict:
        payload = {
            "tenant_id": context.tenant_id,
            "organization_id": context.tenant_id,
            "keys": list(keys),
            "limit": limit,
        }
        return self.transport("POST", f"{self.base_url}/v1/persons/duplicate-candidates", json=payload)

    def get_person(self, context, person_id) -> dict:
        return self.transport(
            "GET", f"{self.base_url}/v1/persons/{person_id}",
            json={"tenant_id": context.tenant_id, "organization_id": context.tenant_id},
        )

    def create_person(self, context, **data) -> dict:
        payload = {"tenant_id": context.tenant_id, "organization_id": context.tenant_id, **data}
        return self.transport("POST", f"{self.base_url}/v1/persons", json=payload)
