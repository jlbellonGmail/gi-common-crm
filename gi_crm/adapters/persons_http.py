"""Adaptador HTTP documentado del subset de PersonsApi usado por gi_crm.

BLOQUEADO / no verificable end-to-end: `gi-common-persons` (milestone
02-07 en `develop`, sin release propio) sólo expone biblioteca Python hoy
(verificado en código, ver docs/tecnica/contrato-persons.md). Sólo se
prueba en tests_crm/test_adapters_http.py contra un transporte simulado.
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
            "organization_id": context.organization_id,
            "keys": list(keys),
            "limit": limit,
        }
        return self.transport("POST", f"{self.base_url}/v1/persons/duplicate-candidates", json=payload)

    def get_person(self, context, person_id) -> dict:
        return self.transport(
            "GET", f"{self.base_url}/v1/persons/{person_id}",
            json={"organization_id": context.organization_id},
        )

    def create_person(self, context, **data) -> dict:
        payload = {"organization_id": context.organization_id, **data}
        return self.transport("POST", f"{self.base_url}/v1/persons", json=payload)
