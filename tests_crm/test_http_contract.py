"""Equivalencia biblioteca/HTTP (spec.md #8): misma operación, misma respuesta funcional.

Requiere el extra `[http]` (fastapi/pydantic). Ver ADR-C05: el contexto de
tenant llega por cabeceras confiables inyectadas por el host autenticado.
"""
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from gi_crm.api import LeadsApi  # noqa: E402
from gi_crm.http.app import create_app  # noqa: E402

HEADERS = {"X-GI-User-Id": "user-a", "X-GI-Organization-Id": "org-a"}


@pytest.fixture
def client(service):
    api = LeadsApi(service, cursor_secret=b"test-secret-please-ignore")
    return TestClient(create_app(api))


def test_missing_context_headers_returns_400(client):
    response = client.post("/v1/leads", json={"title": "Lead"})
    assert response.status_code == 400


def test_create_and_get_lead_over_http(client):
    created = client.post("/v1/leads", json={"title": "Lead HTTP"}, headers=HEADERS).json()
    assert created["status"] == "new"
    fetched = client.get(f"/v1/leads/{created['lead_id']}", headers=HEADERS).json()
    assert fetched["lead_id"] == created["lead_id"]


def test_http_and_library_agree_on_lifecycle(client, service, ctx_a):
    created = client.post("/v1/leads", json={"title": "Lead paralelo"}, headers=HEADERS).json()
    via_service = service.get_lead(ctx_a, created["lead_id"])
    assert str(via_service.lead_id) == created["lead_id"]
    assert via_service.status == created["status"]


def test_not_found_maps_to_404(client):
    response = client.get(
        "/v1/leads/00000000-0000-0000-0000-000000000000", headers=HEADERS
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_openapi_is_reachable(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/v1/leads" in response.json()["paths"]
