"""Vínculo con Persons y búsqueda de duplicados (ADR-C01: sin dependencia dura)."""
import pytest

from gi_crm.errors import PersonsUnavailableError
from gi_crm.memory import InMemoryLeadStore
from gi_crm.service import LeadService

from fakes import FakeCoreApi, FakePersonsApi


def test_find_duplicate_candidates_delegates_to_persons_api(service, ctx_a, persons_api):
    result = service.find_duplicate_candidates(ctx_a, keys={"email": "a@example.com"})
    assert result["contract_version"] == "0.1.0"
    assert result["items"] == []


def test_find_duplicate_candidates_without_persons_api_is_unavailable(ctx_a):
    service = LeadService(InMemoryLeadStore(), FakeCoreApi(allow=True), persons_api=None)
    with pytest.raises(PersonsUnavailableError):
        service.find_duplicate_candidates(ctx_a, keys={"email": "a@example.com"})


def test_find_duplicate_candidates_wraps_persons_failure(ctx_a):
    service = LeadService(InMemoryLeadStore(), FakeCoreApi(allow=True), FakePersonsApi(fail=True))
    with pytest.raises(PersonsUnavailableError):
        service.find_duplicate_candidates(ctx_a, keys={"email": "a@example.com"})


def test_link_person_succeeds_when_person_exists(ctx_a):
    person_id = "11111111-1111-1111-1111-111111111111"
    persons = FakePersonsApi(persons={person_id: {"person_id": person_id}})
    service = LeadService(InMemoryLeadStore(), FakeCoreApi(allow=True), persons)
    lead = service.create_lead(ctx_a, title="Lead")
    updated = service.link_person(ctx_a, lead.lead_id, lead.version, person_id)
    assert str(updated.person_id) == person_id


def test_link_person_without_persons_api_is_unavailable(ctx_a):
    service = LeadService(InMemoryLeadStore(), FakeCoreApi(allow=True), persons_api=None)
    lead = service.create_lead(ctx_a, title="Lead")
    with pytest.raises(PersonsUnavailableError):
        service.link_person(ctx_a, lead.lead_id, lead.version, "00000000-0000-0000-0000-000000000000")


def test_link_person_unknown_person_is_unavailable(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    with pytest.raises(PersonsUnavailableError):
        service.link_person(ctx_a, lead.lead_id, lead.version, "unknown-person")
