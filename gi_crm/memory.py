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

    def _lead(self, org, lead_id):
        lead = self.leads.get((org, lead_id))
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
            key = (lead.organization_id, lead.lead_id)
            if key in self.leads:
                raise VersionConflictError()
            self.leads[key] = lead
            return lead

    def get_lead(self, org, lead_id):
        return self.leads.get((org, lead_id))

    def list_leads(self, org, *, status=None, owner_user_id=None, source_id=None, person_id=None, limit=20, after=None):
        with self._lock:
            items = [lead for (o, _), lead in self.leads.items() if o == org]
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
            current = self._lead(lead.organization_id, lead.lead_id)
            if current.version != expected_version:
                raise VersionConflictError()
            updated = replace(
                lead, version=current.version + 1, created_at=current.created_at, updated_at=utcnow(),
            )
            self.leads[(lead.organization_id, lead.lead_id)] = updated
            return updated

    def append_status_event(self, event):
        with self._lock:
            self._lead(event.organization_id, event.lead_id)
            self.status_events.append(event)

    def list_status_events(self, org, lead_id):
        return sorted(
            (event for event in self.status_events if event.organization_id == org and event.lead_id == lead_id),
            key=lambda event: event.occurred_at,
        )

    def append_activity(self, activity):
        with self._lock:
            self._lead(activity.organization_id, activity.lead_id)
            self.activities.append(activity)
            return activity

    def list_activities(self, org, lead_id):
        return sorted(
            (a for a in self.activities if a.organization_id == org and a.lead_id == lead_id),
            key=lambda a: a.occurred_at,
        )

    def append_assignment(self, event):
        with self._lock:
            self._lead(event.organization_id, event.lead_id)
            self.assignments.append(event)

    def list_assignments(self, org, lead_id):
        return sorted(
            (event for event in self.assignments if event.organization_id == org and event.lead_id == lead_id),
            key=lambda event: event.occurred_at,
        )

    def add_external_reference(self, reference):
        with self._lock:
            self._lead(reference.organization_id, reference.lead_id)
            key = (reference.organization_id, reference.vertical_code, reference.external_type, reference.external_id)
            existing_keys = {
                (r.organization_id, r.vertical_code, r.external_type, r.external_id)
                for r in self.external_references.values()
            }
            if key in existing_keys:
                raise DuplicateExternalReferenceError()
            self.external_references[reference.reference_id] = reference
            return reference

    def list_external_references(self, org, lead_id):
        return [
            r for r in self.external_references.values()
            if r.organization_id == org and r.lead_id == lead_id
        ]
