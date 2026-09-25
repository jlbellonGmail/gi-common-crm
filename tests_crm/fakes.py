"""Fakes de CoreApi/PersonsApi para pruebas de dominio sin transporte real."""


class FakeCoreApi:
    def __init__(self, allow=True, contract_version="0.1.0", fail=False):
        self.allow = allow
        self.contract_version = contract_version
        self.fail = fail
        self.calls = []

    def authorize(self, user_id, tenant_id, permission, location_id=None):
        self.calls.append((user_id, tenant_id, permission, location_id))
        if self.fail:
            raise RuntimeError("core unavailable (simulated)")
        return {
            "contract_version": self.contract_version,
            "allowed": self.allow,
            "reason": None if self.allow else "denied",
            "context": {"user_id": user_id, "tenant_id": tenant_id},
        }


class FakePersonsApi:
    def __init__(self, persons=None, fail=False):
        self.persons = persons or {}
        self.fail = fail

    def get_person(self, context, person_id):
        if self.fail:
            raise RuntimeError("persons unavailable (simulated)")
        pid = str(person_id)
        if pid not in self.persons:
            raise KeyError(pid)
        return self.persons[pid]

    def find_duplicate_candidates(self, context, *, keys, limit=20):
        if self.fail:
            raise RuntimeError("persons unavailable (simulated)")
        return {"contract_version": "0.1.0", "items": []}

    def create_person(self, context, **data):
        if self.fail:
            raise RuntimeError("persons unavailable (simulated)")
        return {"contract_version": "0.1.0", "person_id": "generated", **data}
