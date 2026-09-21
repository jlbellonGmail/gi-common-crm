"""Cardinalidad Lead<->Person (ADR-C01): una Person puede tener N Leads sin unicidad implícita."""
from gi_crm.memory import InMemoryLeadStore
from gi_crm.service import LeadService

from fakes import FakeCoreApi, FakePersonsApi


def test_same_person_can_have_multiple_leads(ctx_a):
    person_id = "11111111-1111-1111-1111-111111111111"
    persons = FakePersonsApi(persons={person_id: {"person_id": person_id}})
    service = LeadService(InMemoryLeadStore(), FakeCoreApi(allow=True), persons)
    lead_one = service.create_lead(ctx_a, title="Interés en dental")
    lead_two = service.create_lead(ctx_a, title="Interés en legal")
    lead_one = service.link_person(ctx_a, lead_one.lead_id, lead_one.version, person_id)
    lead_two = service.link_person(ctx_a, lead_two.lead_id, lead_two.version, person_id)
    assert lead_one.person_id == lead_two.person_id
    leads_for_person = service.list_leads(ctx_a, person_id=person_id)
    assert len(leads_for_person) == 2
