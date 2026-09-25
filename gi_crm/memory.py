"""Reference in-memory adapter used only for deterministic tests and examples."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from threading import RLock

from .errors import DuplicateExternalReferenceError, NotFoundError, VersionConflictError
from .models import utcnow


class InMemoryLeadStore:
    def __init__(self, audit_sink=None):
        self._lock = RLock()
        self.leads = {}
        self.status_events = []
        self.activities = []
        self.assignments = []
        self.external_references = {}
        self.audit = []
        self.audit_sink = audit_sink

    def _lead(self, tenant_id, lead_id):
        lead = self.leads.get((tenant_id, lead_id))
        if lead is None:
            raise NotFoundError()
        return lead

    def _event(self, event):
        if self.audit_sink:
            self.audit_sink.append(event)
        self.audit.append(event)

    @contextmanager
    def transaction(self):
        with self._lock:
            snapshot = (
                deepcopy(self.leads), deepcopy(self.status_events), deepcopy(self.activities),
                deepcopy(self.assignments), deepcopy(self.external_references), deepcopy(self.audit),
            )
            try:
                yield
            except Exception:
                (
                    self.leads, self.status_events, self.activities,
                    self.assignments, self.external_references, self.audit,
                ) = snapshot
                raise

    def create_lead(self, lead):
        with self._lock:
            key = (lead.tenant_id, lead.lead_id)
            if key in self.leads:
                raise VersionConflictError()
            self.leads[key] = lead
            return lead

    def get_lead(self, tenant_id, lead_id):
        return self.leads.get((tenant_id, lead_id))

    def list_leads(self, tenant_id, *, status=None, owner_user_id=None, source_id=None, person_id=None, limit=20, after=None):
        with self._lock:
            items = [lead for (t, _), lead in self.leads.items() if t == tenant_id]
            if status is not None:
                items = [lead for lead in items if lead.status == status]
            if owner_user_id is not None:
                items = [lead for lead in items if lead.owner_user_id == owner_user_id]
            if source_id is not None:
                items = [lead for lead in items if lead.source_id == source_id]
            if person_id is not None:
                items = [lead for lead in items if lead.person_id == person_id]
            items = sorted(items, key=lambda lead: str(lead.lead_id))
            if after:
                items = [lead for lead in items if str(lead.lead_id) > str(after)]
            return items[:limit]

    def update_lead(self, lead, expected_version):
        with self._lock:
            current = self._lead(lead.tenant_id, lead.lead_id)
            if current.version != expected_version:
                raise VersionConflictError()
            updated = replace(
                lead, version=current.version + 1, created_at=current.created_at, updated_at=utcnow(),
            )
            self.leads[(lead.tenant_id, lead.lead_id)] = updated
            return updated

    def append_status_event(self, event):
        with self._lock:
            self._lead(event.tenant_id, event.lead_id)
            self.status_events.append(event)

    def list_status_events(self, tenant_id, lead_id):
        return sorted(
            (event for event in self.status_events if event.tenant_id == tenant_id and event.lead_id == lead_id),
            key=lambda event: event.occurred_at,
        )

    def append_activity(self, activity):
        with self._lock:
            self._lead(activity.tenant_id, activity.lead_id)
            self.activities.append(activity)
            return activity

    def list_activities(self, tenant_id, lead_id):
        return sorted(
            (a for a in self.activities if a.tenant_id == tenant_id and a.lead_id == lead_id),
            key=lambda a: a.occurred_at,
        )

    def append_assignment(self, event):
        with self._lock:
            self._lead(event.tenant_id, event.lead_id)
            self.assignments.append(event)

    def list_assignments(self, tenant_id, lead_id):
        return sorted(
            (event for event in self.assignments if event.tenant_id == tenant_id and event.lead_id == lead_id),
            key=lambda event: event.occurred_at,
        )

    def add_external_reference(self, reference):
        with self._lock:
            self._lead(reference.tenant_id, reference.lead_id)
            key = (reference.tenant_id, reference.vertical_code, reference.external_type, reference.external_id)
            existing_keys = {
                (r.tenant_id, r.vertical_code, r.external_type, r.external_id)
                for r in self.external_references.values()
            }
            if key in existing_keys:
                raise DuplicateExternalReferenceError()
            self.external_references[reference.reference_id] = reference
            return reference

    def list_external_references(self, tenant_id, lead_id):
        return [
            r for r in self.external_references.values()
            if r.tenant_id == tenant_id and r.lead_id == lead_id
        ]
