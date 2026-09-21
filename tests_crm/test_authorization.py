"""Autorización fail-closed contra CoreApi (ADR-C03): nunca se permite por defecto."""
import pytest

from gi_crm.errors import CoreUnavailableError, ForbiddenError, UnsupportedCoreContractError
from gi_crm.memory import InMemoryLeadStore
from gi_crm.models import RequestContext
from gi_crm.service import LeadService

from fakes import FakeCoreApi


def test_denied_by_core_raises_forbidden(ctx_a):
    service = LeadService(InMemoryLeadStore(), FakeCoreApi(allow=False))
    with pytest.raises(ForbiddenError):
        service.create_lead(ctx_a, title="Lead")


def test_core_unavailable_never_authorizes_by_default(ctx_a):
    service = LeadService(InMemoryLeadStore(), FakeCoreApi(fail=True))
    with pytest.raises(CoreUnavailableError):
        service.create_lead(ctx_a, title="Lead")


def test_unsupported_contract_version_is_rejected(ctx_a):
    service = LeadService(InMemoryLeadStore(), FakeCoreApi(allow=True, contract_version="9.9.9"))
    with pytest.raises(UnsupportedCoreContractError):
        service.create_lead(ctx_a, title="Lead")


def test_context_echo_mismatch_is_forbidden(ctx_a):
    class TamperingCoreApi:
        def authorize(self, user_id, organization_id, permission, location_id=None):
            return {
                "contract_version": "0.1.0",
                "allowed": True,
                "reason": None,
                "context": {"user_id": "someone-else", "organization_id": organization_id},
            }

    service = LeadService(InMemoryLeadStore(), TamperingCoreApi())
    with pytest.raises(ForbiddenError):
        service.create_lead(ctx_a, title="Lead")


def test_authorize_is_called_with_location_id_when_present():
    ctx = RequestContext(user_id="user-a", organization_id="org-a", location_id="loc-1")
    core = FakeCoreApi(allow=True)
    service = LeadService(InMemoryLeadStore(), core)
    service.create_lead(ctx, title="Lead")
    assert core.calls[0] == ("user-a", "org-a", "crm:lead:write", "loc-1")


def test_trusted_context_is_required():
    with pytest.raises(ValueError):
        RequestContext(user_id="user-a", organization_id="org-a", trusted=False)
