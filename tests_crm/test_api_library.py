"""Fachada JSON-safe LeadsApi: paginación por cursor y errores mapeados (spec.md #7)."""
import pytest

from gi_crm.api import LeadsApi
from gi_crm.errors import ValidationError


@pytest.fixture
def api(service):
    return LeadsApi(service, cursor_secret=b"test-secret-please-ignore")


def test_create_and_get_lead_are_json_safe(api, ctx_a):
    created = api.create_lead(ctx_a, title="Lead API")
    assert isinstance(created["lead_id"], str)
    assert isinstance(created["created_at"], str)
    fetched = api.get_lead(ctx_a, created["lead_id"])
    assert fetched["lead_id"] == created["lead_id"]


def test_list_leads_paginates_with_cursor(api, ctx_a):
    for i in range(3):
        api.create_lead(ctx_a, title=f"Lead {i}")
    page = api.list_leads(ctx_a, limit=2)
    assert len(page["items"]) == 2
    assert page["next_cursor"] is not None
    next_page = api.list_leads(ctx_a, limit=2, cursor=page["next_cursor"])
    assert len(next_page["items"]) == 1
    assert next_page["next_cursor"] is None


def test_error_maps_crm_error_to_code(api, ctx_a):
    payload = api.error(ValidationError())
    assert payload == {"code": "VALIDATION_ERROR", "message": "The request is invalid."}


def test_error_maps_unknown_exception_generically(api):
    payload = api.error(RuntimeError("boom"))
    assert payload["code"] == "INTERNAL_ERROR"


def test_cursor_rejects_tampering(api, ctx_a):
    for i in range(3):
        api.create_lead(ctx_a, title=f"Lead {i}")
    page = api.list_leads(ctx_a, limit=2)
    tampered = page["next_cursor"][:-1] + ("A" if page["next_cursor"][-1] != "A" else "B")
    with pytest.raises(ValidationError):
        api.list_leads(ctx_a, limit=2, cursor=tampered)


def test_many_valid_cursors_round_trip_without_signature_delimiter_collisions(api, ctx_a):
    for i in range(100):
        api.create_lead(ctx_a, title=f"Cursor lead {i}-a")
        api.create_lead(ctx_a, title=f"Cursor lead {i}-b")
        page = api.list_leads(ctx_a, limit=1)
        assert page["next_cursor"] is not None
        assert len(api.list_leads(ctx_a, limit=1, cursor=page["next_cursor"])["items"]) == 1
