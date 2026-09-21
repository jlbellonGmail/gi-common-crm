"""Concurrencia optimista: expected_version obsoleto siempre falla (ver spec.md #6)."""
import pytest

from gi_crm.errors import VersionConflictError


def test_update_lead_rejects_stale_version(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    service.update_lead(ctx_a, lead.lead_id, lead.version, title="Lead actualizado")
    with pytest.raises(VersionConflictError):
        service.update_lead(ctx_a, lead.lead_id, lead.version, title="Otra vez")


def test_change_status_rejects_stale_version(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    service.change_status(ctx_a, lead.lead_id, lead.version, "contacted")
    # "archived" sigue siendo una transición válida desde "contacted" (el
    # estado real tras la primera llamada): esto aísla el conflicto de
    # versión del error de transición inválida.
    with pytest.raises(VersionConflictError):
        service.change_status(ctx_a, lead.lead_id, lead.version, "archived")


def test_assign_lead_rejects_stale_version(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    service.assign_lead(ctx_a, lead.lead_id, lead.version, "user-x")
    with pytest.raises(VersionConflictError):
        service.assign_lead(ctx_a, lead.lead_id, lead.version, "user-y")
