"""Aislamiento multitenant negativo (spec.md #4): org A nunca ve ni afecta datos de org B."""
import pytest

from gi_crm.errors import NotFoundError


def test_org_a_cannot_read_org_b_lead(service, ctx_a, ctx_b):
    lead = service.create_lead(ctx_b, title="Lead de B")
    with pytest.raises(NotFoundError):
        service.get_lead(ctx_a, lead.lead_id)


def test_org_a_list_leads_never_returns_org_b_items(service, ctx_a, ctx_b):
    service.create_lead(ctx_b, title="Lead de B")
    service.create_lead(ctx_a, title="Lead de A")
    items = service.list_leads(ctx_a)
    assert all(item.tenant_id == ctx_a.tenant_id for item in items)
    assert len(items) == 1


def test_org_a_cannot_update_org_b_lead(service, ctx_a, ctx_b):
    lead = service.create_lead(ctx_b, title="Lead de B")
    with pytest.raises(NotFoundError):
        service.update_lead(ctx_a, lead.lead_id, lead.version, title="hijack")


def test_org_a_cannot_change_status_of_org_b_lead(service, ctx_a, ctx_b):
    lead = service.create_lead(ctx_b, title="Lead de B")
    with pytest.raises(NotFoundError):
        service.change_status(ctx_a, lead.lead_id, lead.version, "contacted")


def test_org_a_cannot_assign_org_b_lead(service, ctx_a, ctx_b):
    lead = service.create_lead(ctx_b, title="Lead de B")
    with pytest.raises(NotFoundError):
        service.assign_lead(ctx_a, lead.lead_id, lead.version, "user-x")


def test_org_a_cannot_add_activity_to_org_b_lead(service, ctx_a, ctx_b):
    lead = service.create_lead(ctx_b, title="Lead de B")
    with pytest.raises(NotFoundError):
        service.add_activity(ctx_a, lead.lead_id, kind="note", notes="espionaje")


def test_org_a_cannot_link_person_on_org_b_lead(service, ctx_a, ctx_b):
    lead = service.create_lead(ctx_b, title="Lead de B")
    with pytest.raises(NotFoundError):
        service.link_person(ctx_a, lead.lead_id, lead.version, "00000000-0000-0000-0000-000000000000")


def test_org_a_cannot_convert_org_b_lead(service, ctx_a, ctx_b):
    lead = service.create_lead(ctx_b, title="Lead de B")
    with pytest.raises(NotFoundError):
        service.convert_lead(ctx_a, lead.lead_id, vertical_code="dental", external_type="patient", external_id="123")


def test_status_history_is_scoped_per_tenant(service, ctx_a, ctx_b):
    lead_a = service.create_lead(ctx_a, title="A")
    service.change_status(ctx_a, lead_a.lead_id, lead_a.version, "contacted")
    lead_b = service.create_lead(ctx_b, title="B")
    with pytest.raises(NotFoundError):
        service.list_status_history(ctx_a, lead_b.lead_id)
