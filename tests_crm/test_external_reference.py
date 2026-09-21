"""Referencias externas de vertical y conversión comercial (spec.md #9)."""
import pytest

from gi_crm.errors import DuplicateExternalReferenceError, InvalidTransitionError


def test_add_external_reference_rejects_duplicate(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    service.add_external_reference(ctx_a, lead.lead_id, vertical_code="dental", external_type="patient", external_id="123")
    with pytest.raises(DuplicateExternalReferenceError):
        service.add_external_reference(ctx_a, lead.lead_id, vertical_code="dental", external_type="patient", external_id="123")


def test_same_external_id_allowed_across_verticals(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    service.add_external_reference(ctx_a, lead.lead_id, vertical_code="dental", external_type="patient", external_id="123")
    service.add_external_reference(ctx_a, lead.lead_id, vertical_code="law", external_type="client", external_id="123")
    refs = service.list_external_references(ctx_a, lead.lead_id)
    assert len(refs) == 2


def test_convert_lead_requires_won_status(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    with pytest.raises(InvalidTransitionError):
        service.convert_lead(ctx_a, lead.lead_id, vertical_code="dental", external_type="patient", external_id="123")


def test_convert_lead_creates_reference_once_won(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    lead = service.change_status(ctx_a, lead.lead_id, lead.version, "contacted")
    lead = service.change_status(ctx_a, lead.lead_id, lead.version, "qualified")
    lead = service.change_status(ctx_a, lead.lead_id, lead.version, "in_progress")
    lead = service.change_status(ctx_a, lead.lead_id, lead.version, "won", reason="cerrado")
    reference = service.convert_lead(ctx_a, lead.lead_id, vertical_code="dental", external_type="patient", external_id="999")
    assert reference.external_id == "999"
