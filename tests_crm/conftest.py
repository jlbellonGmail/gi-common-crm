import pytest

from gi_crm.memory import InMemoryLeadStore
from gi_crm.models import RequestContext
from gi_crm.service import LeadService

from fakes import FakeCoreApi, FakePersonsApi


@pytest.fixture
def core_api():
    return FakeCoreApi(allow=True)


@pytest.fixture
def persons_api():
    return FakePersonsApi()


@pytest.fixture
def store():
    return InMemoryLeadStore()


@pytest.fixture
def service(store, core_api, persons_api):
    return LeadService(store, core_api, persons_api)


@pytest.fixture
def ctx_a():
    return RequestContext(user_id="user-a", tenant_id="00000000-0000-0000-0000-00000000000a")


@pytest.fixture
def ctx_b():
    return RequestContext(user_id="user-b", tenant_id="00000000-0000-0000-0000-00000000000b")
