"""Adaptadores CoreHttpApi/PersonsHttpApi contra un transporte simulado.

BLOQUEADO/no verificable end-to-end (ver docs/tecnica/contrato-core.md y
contrato-persons.md): ni gi-platform-core ni gi-common-persons exponen HTTP
hoy. Estas pruebas sólo verifican que el adaptador arma la petición y
devuelve la respuesta del transporte inyectado, sin acoplarse a ningún
cliente HTTP concreto.
"""
from gi_crm.adapters.core_http import CoreHttpApi
from gi_crm.adapters.persons_http import PersonsHttpApi


def test_core_http_api_authorize_calls_expected_endpoint():
    calls = []

    def transport(method, url, *, json=None):
        calls.append((method, url, json))
        return {"contract_version": "0.1.0", "allowed": True, "reason": None, "context": json}

    api = CoreHttpApi("http://core.example/", transport)
    result = api.authorize("user-a", "00000000-0000-0000-0000-00000000000a", "crm:lead:write", "loc-1")
    assert calls[0][0] == "POST"
    assert calls[0][1] == "http://core.example/v1/authorize"
    assert calls[0][2]["permission"] == "crm:lead:write"
    assert result["allowed"] is True


def test_persons_http_api_find_duplicate_candidates():
    def transport(method, url, *, json=None):
        assert method == "POST"
        assert url == "http://persons.example/v1/persons/duplicate-candidates"
        return {"contract_version": "0.1.0", "items": []}

    api = PersonsHttpApi("http://persons.example", transport)

    class Ctx:
        tenant_id = "00000000-0000-0000-0000-00000000000a"

    result = api.find_duplicate_candidates(Ctx(), keys={"email": "a@example.com"})
    assert result["items"] == []


def test_persons_http_api_get_person():
    def transport(method, url, *, json=None):
        assert method == "GET"
        assert url.endswith("/v1/persons/p-1")
        return {"person_id": "p-1"}

    api = PersonsHttpApi("http://persons.example", transport)

    class Ctx:
        tenant_id = "00000000-0000-0000-0000-00000000000a"

    result = api.get_person(Ctx(), "p-1")
    assert result["person_id"] == "p-1"


def test_persons_http_api_create_person():
    def transport(method, url, *, json=None):
        assert method == "POST"
        assert url == "http://persons.example/v1/persons"
        assert json["organization_id"] == "00000000-0000-0000-0000-00000000000a"
        return {"person_id": "generated", **json}

    api = PersonsHttpApi("http://persons.example", transport)

    class Ctx:
        tenant_id = "00000000-0000-0000-0000-00000000000a"

    result = api.create_person(Ctx(), display_name="Ada")
    assert result["display_name"] == "Ada"
