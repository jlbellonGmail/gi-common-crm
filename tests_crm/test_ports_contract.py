"""Forma real de los puertos: los adaptadores de referencia calzan por duck typing."""
from gi_crm.adapters.core_http import CoreHttpApi
from gi_crm.adapters.persons_http import PersonsHttpApi
from gi_crm.memory import InMemoryLeadStore
from gi_crm.ports import LeadStore


def test_in_memory_store_implements_lead_store_shape():
    for name in LeadStore.__protocol_attrs__ if hasattr(LeadStore, "__protocol_attrs__") else (
        "create_lead", "get_lead", "list_leads", "update_lead", "append_status_event",
        "list_status_events", "append_activity", "list_activities", "append_assignment",
        "list_assignments", "add_external_reference", "list_external_references",
    ):
        assert callable(getattr(InMemoryLeadStore, name, None)), f"missing {name}"


def test_core_http_api_implements_authorize():
    api = CoreHttpApi("http://core.example", transport=lambda *a, **k: {})
    assert callable(api.authorize)


def test_persons_http_api_implements_persons_subset():
    api = PersonsHttpApi("http://persons.example", transport=lambda *a, **k: {})
    assert callable(api.find_duplicate_candidates)
    assert callable(api.get_person)
    assert callable(api.create_person)
