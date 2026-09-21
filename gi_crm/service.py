"""Application use cases; every operation authorizes before tenant access.

Ver docs/tecnica/arquitectura-crm.md (ADR-C03, ADR-C06) y
runs/milestone-leads-core-implementation/spec.md para los criterios de
aceptación que este módulo implementa.
"""
from contextlib import nullcontext
from dataclasses import replace
from uuid import UUID, uuid4

from .authorization import Authorizer
from .errors import (
    AuditFailureError,
    InvalidTransitionError,
    PersonsUnavailableError,
    ValidationError,
    NotFoundError,
)
from .models import (
    Lead,
    LeadActivity,
    LeadAssignmentEvent,
    LeadAudit,
    LeadExternalReference,
    LeadStatusEvent,
    VALID_TRANSITIONS,
    utcnow,
)

ACTIVITY_KINDS = frozenset({"note", "call", "email", "meeting", "other"})


class LeadService:
    def __init__(self, store, core_api, persons_api=None, audit_sink=None):
        self.store = store
        self.auth = Authorizer(core_api)
        self.persons_api = persons_api
        self.audit_sink = audit_sink

    def _audit(self, ctx, lead_id, action, outcome, version):
        event = LeadAudit(
            uuid4(), ctx.organization_id, lead_id, ctx.user_id, action,
            utcnow(), ctx.correlation_id, outcome, version,
        )
        try:
            if self.audit_sink:
                self.audit_sink.append(event)
            elif hasattr(self.store, "_event"):
                self.store._event(event)
        except Exception as exc:
            raise AuditFailureError() from exc

    def _transaction(self):
        return self.store.transaction() if hasattr(self.store, "transaction") else nullcontext()

    def _uuid(self, value) -> UUID:
        return value if isinstance(value, UUID) else UUID(str(value))

    # -- Lead CRUD -----------------------------------------------------

    def create_lead(self, ctx, *, title, description=None, person_id=None, source_id=None, owner_user_id=None):
        self.auth.require(ctx, "crm:lead:write")
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ValidationError()
        lead = Lead(
            uuid4(), ctx.organization_id, "new",
            self._uuid(person_id) if person_id else None,
            self._uuid(source_id) if source_id else None,
            owner_user_id, title.strip(), description,
        )
        with self._transaction():
            result = self.store.create_lead(lead)
            self._audit(ctx, result.lead_id, "lead.create", "success", result.version)
            return result

    def get_lead(self, ctx, lead_id):
        self.auth.require(ctx, "crm:lead:read")
        lead = self.store.get_lead(ctx.organization_id, self._uuid(lead_id))
        if lead is None:
            raise NotFoundError()
        return lead

    def list_leads(self, ctx, *, status=None, owner_user_id=None, source_id=None, person_id=None, limit=20, after=None):
        self.auth.require(ctx, "crm:lead:read")
        if limit < 1 or limit > 101:
            raise ValidationError()
        return self.store.list_leads(
            ctx.organization_id,
            status=status,
            owner_user_id=owner_user_id,
            source_id=self._uuid(source_id) if source_id else None,
            person_id=self._uuid(person_id) if person_id else None,
            limit=limit,
            after=after,
        )

    def update_lead(self, ctx, lead_id, expected_version, **fields):
        self.auth.require(ctx, "crm:lead:write")
        current = self.get_lead(ctx, lead_id)
        allowed = {"title", "description", "source_id", "person_id"}
        if set(fields) - allowed:
            raise ValidationError()
        if "title" in fields and (not fields["title"] or not fields["title"].strip() or len(fields["title"]) > 200):
            raise ValidationError()
        updated = replace(current, **fields)
        with self._transaction():
            result = self.store.update_lead(updated, expected_version)
            self._audit(ctx, lead_id, "lead.update", "success", result.version)
            return result

    # -- Ciclo de vida comercial ----------------------------------------

    def change_status(self, ctx, lead_id, expected_version, to_status, *, reason=None):
        self.auth.require(ctx, "crm:lead:status:write")
        current = self.get_lead(ctx, lead_id)
        if to_status not in VALID_TRANSITIONS.get(current.status, frozenset()):
            raise InvalidTransitionError()
        close_reason = reason if to_status in ("won", "lost") else current.close_reason
        updated = replace(current, status=to_status, close_reason=close_reason)
        event = LeadStatusEvent(uuid4(), ctx.organization_id, self._uuid(lead_id), current.status, to_status, ctx.user_id, reason=reason)
        with self._transaction():
            result = self.store.update_lead(updated, expected_version)
            self.store.append_status_event(event)
            self._audit(ctx, lead_id, "lead.status_change", "success", result.version)
            return result

    def close_lead(self, ctx, lead_id, expected_version, outcome, *, reason=None):
        if outcome not in ("won", "lost"):
            raise ValidationError()
        return self.change_status(ctx, lead_id, expected_version, outcome, reason=reason)

    def list_status_history(self, ctx, lead_id):
        self.auth.require(ctx, "crm:lead:read")
        self.get_lead(ctx, lead_id)
        return self.store.list_status_events(ctx.organization_id, self._uuid(lead_id))

    # -- Asignación -------------------------------------------------------

    def assign_lead(self, ctx, lead_id, expected_version, to_user_id):
        self.auth.require(ctx, "crm:lead:assign:write")
        current = self.get_lead(ctx, lead_id)
        if not to_user_id:
            raise ValidationError()
        updated = replace(current, owner_user_id=to_user_id)
        event = LeadAssignmentEvent(uuid4(), ctx.organization_id, self._uuid(lead_id), current.owner_user_id, to_user_id, ctx.user_id)
        with self._transaction():
            result = self.store.update_lead(updated, expected_version)
            self.store.append_assignment(event)
            self._audit(ctx, lead_id, "lead.assign", "success", result.version)
            return result

    def reassign_lead(self, ctx, lead_id, expected_version, to_user_id):
        return self.assign_lead(ctx, lead_id, expected_version, to_user_id)

    def list_assignments(self, ctx, lead_id):
        self.auth.require(ctx, "crm:lead:read")
        self.get_lead(ctx, lead_id)
        return self.store.list_assignments(ctx.organization_id, self._uuid(lead_id))

    # -- Actividad --------------------------------------------------------

    def add_activity(self, ctx, lead_id, *, kind, notes=""):
        self.auth.require(ctx, "crm:lead:activity:write")
        self.get_lead(ctx, lead_id)
        if kind not in ACTIVITY_KINDS:
            raise ValidationError()
        activity = LeadActivity(uuid4(), ctx.organization_id, self._uuid(lead_id), ctx.user_id, kind, notes)
        with self._transaction():
            result = self.store.append_activity(activity)
            self._audit(ctx, lead_id, "lead.activity.add", "success", None)
            return result

    def list_activities(self, ctx, lead_id):
        self.auth.require(ctx, "crm:lead:activity:read")
        self.get_lead(ctx, lead_id)
        return self.store.list_activities(ctx.organization_id, self._uuid(lead_id))

    # -- Persons: vínculo y duplicados -------------------------------------

    def link_person(self, ctx, lead_id, expected_version, person_id):
        self.auth.require(ctx, "crm:lead:link:write")
        if self.persons_api is None:
            raise PersonsUnavailableError()
        current = self.get_lead(ctx, lead_id)
        try:
            self.persons_api.get_person(ctx, person_id)
        except Exception as exc:
            raise PersonsUnavailableError() from exc
        updated = replace(current, person_id=self._uuid(person_id))
        with self._transaction():
            result = self.store.update_lead(updated, expected_version)
            self._audit(ctx, lead_id, "lead.link_person", "success", result.version)
            return result

    def find_duplicate_candidates(self, ctx, *, keys, limit=20):
        self.auth.require(ctx, "crm:lead:link:write")
        if self.persons_api is None:
            raise PersonsUnavailableError()
        try:
            return self.persons_api.find_duplicate_candidates(ctx, keys=keys, limit=limit)
        except Exception as exc:
            raise PersonsUnavailableError() from exc

    # -- Conversión y referencias externas de vertical ---------------------

    def add_external_reference(self, ctx, lead_id, *, vertical_code, external_type, external_id):
        self.auth.require(ctx, "crm:lead:external-reference:write")
        self.get_lead(ctx, lead_id)
        if not vertical_code or not external_type or not external_id:
            raise ValidationError()
        reference = LeadExternalReference(uuid4(), ctx.organization_id, self._uuid(lead_id), vertical_code, external_type, external_id)
        with self._transaction():
            result = self.store.add_external_reference(reference)
            self._audit(ctx, lead_id, "lead.external_reference.add", "success", None)
            return result

    def list_external_references(self, ctx, lead_id):
        self.auth.require(ctx, "crm:lead:read")
        self.get_lead(ctx, lead_id)
        return self.store.list_external_references(ctx.organization_id, self._uuid(lead_id))

    def convert_lead(self, ctx, lead_id, *, vertical_code, external_type, external_id):
        self.auth.require(ctx, "crm:lead:convert:write")
        current = self.get_lead(ctx, lead_id)
        if current.status != "won":
            raise InvalidTransitionError()
        if not vertical_code or not external_type or not external_id:
            raise ValidationError()
        reference = LeadExternalReference(uuid4(), ctx.organization_id, self._uuid(lead_id), vertical_code, external_type, external_id)
        with self._transaction():
            result = self.store.add_external_reference(reference)
            self._audit(ctx, lead_id, "lead.convert", "success", current.version)
            return result
