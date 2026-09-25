"""Versioned JSON-safe facade without HTTP assumptions."""
import base64
import hashlib
import hmac
import json
from uuid import UUID

from .errors import CrmError, ValidationError
from .models import json_value

CONTRACT_VERSION = "0.1.0"


class CursorCodec:
    def __init__(self, secret: bytes):
        if not secret:
            raise ValueError("cursor secret required")
        self.secret = secret

    def encode(self, org, filters, last_id):
        payload = json.dumps(
            {"o": org, "f": filters, "l": str(last_id)}, sort_keys=True, separators=(",", ":")
        ).encode()
        sig = hmac.new(self.secret, payload, hashlib.sha256).digest()
        payload_token = base64.urlsafe_b64encode(payload).decode().rstrip("=")
        signature_token = base64.urlsafe_b64encode(sig).decode().rstrip("=")
        return f"{payload_token}.{signature_token}"

    def decode(self, org, filters, token):
        try:
            payload_token, signature_token = token.split(".", 1)
            payload = base64.urlsafe_b64decode(payload_token + "=" * ((4 - len(payload_token) % 4) % 4))
            sig = base64.urlsafe_b64decode(signature_token + "=" * ((4 - len(signature_token) % 4) % 4))
            if not hmac.compare_digest(sig, hmac.new(self.secret, payload, hashlib.sha256).digest()):
                raise ValueError
            data = json.loads(payload)
            if data["o"] != org or data["f"] != filters:
                raise ValueError
            return UUID(data["l"])
        except Exception as exc:
            raise ValidationError() from exc


def summary(lead):
    return json_value({
        "contract_version": CONTRACT_VERSION,
        "tenant_id": lead.tenant_id,
        "lead_id": lead.lead_id,
        "status": lead.status,
        "person_id": lead.person_id,
        "source_id": lead.source_id,
        "owner_user_id": lead.owner_user_id,
        "title": lead.title,
        "description": lead.description,
        "close_reason": lead.close_reason,
        "version": lead.version,
        "created_at": lead.created_at,
        "updated_at": lead.updated_at,
    })


def public_status_event(event):
    return json_value({
        "contract_version": CONTRACT_VERSION,
        "event_id": event.event_id,
        "lead_id": event.lead_id,
        "from_status": event.from_status,
        "to_status": event.to_status,
        "actor_user_id": event.actor_user_id,
        "occurred_at": event.occurred_at,
        "reason": event.reason,
    })


def public_activity(activity):
    return json_value({
        "contract_version": CONTRACT_VERSION,
        "activity_id": activity.activity_id,
        "lead_id": activity.lead_id,
        "actor_user_id": activity.actor_user_id,
        "kind": activity.kind,
        "notes": activity.notes,
        "occurred_at": activity.occurred_at,
    })


def public_assignment(event):
    return json_value({
        "contract_version": CONTRACT_VERSION,
        "assignment_id": event.assignment_id,
        "lead_id": event.lead_id,
        "from_user_id": event.from_user_id,
        "to_user_id": event.to_user_id,
        "actor_user_id": event.actor_user_id,
        "occurred_at": event.occurred_at,
    })


def public_external_reference(reference):
    return json_value({
        "contract_version": CONTRACT_VERSION,
        "reference_id": reference.reference_id,
        "lead_id": reference.lead_id,
        "vertical_code": reference.vertical_code,
        "external_type": reference.external_type,
        "external_id": reference.external_id,
        "created_at": reference.created_at,
    })


class LeadsApi:
    def __init__(self, service, cursor_secret: bytes):
        self.service = service
        self.cursors = CursorCodec(cursor_secret)

    def create_lead(self, context, **data):
        return summary(self.service.create_lead(context, **data))

    def get_lead(self, context, lead_id):
        return summary(self.service.get_lead(context, UUID(str(lead_id))))

    def list_leads(self, context, *, limit=20, cursor=None, filters=""):
        after = self.cursors.decode(context.tenant_id, filters, cursor) if cursor else None
        items = self.service.list_leads(context, limit=limit + 1, after=after)
        more = len(items) > limit
        items = items[:limit]
        return {
            "contract_version": CONTRACT_VERSION,
            "items": [summary(lead) for lead in items],
            "next_cursor": (
                self.cursors.encode(context.tenant_id, filters, items[-1].lead_id)
                if more and items else None
            ),
        }

    def update_lead(self, context, lead_id, expected_version, **fields):
        return summary(self.service.update_lead(context, UUID(str(lead_id)), expected_version, **fields))

    def change_status(self, context, lead_id, expected_version, to_status, **kwargs):
        return summary(self.service.change_status(context, UUID(str(lead_id)), expected_version, to_status, **kwargs))

    def close_lead(self, context, lead_id, expected_version, outcome, **kwargs):
        return summary(self.service.close_lead(context, UUID(str(lead_id)), expected_version, outcome, **kwargs))

    def list_status_history(self, context, lead_id):
        items = self.service.list_status_history(context, UUID(str(lead_id)))
        return {"contract_version": CONTRACT_VERSION, "items": [public_status_event(e) for e in items]}

    def assign_lead(self, context, lead_id, expected_version, to_user_id):
        return summary(self.service.assign_lead(context, UUID(str(lead_id)), expected_version, to_user_id))

    def reassign_lead(self, context, lead_id, expected_version, to_user_id):
        return summary(self.service.reassign_lead(context, UUID(str(lead_id)), expected_version, to_user_id))

    def list_assignments(self, context, lead_id):
        items = self.service.list_assignments(context, UUID(str(lead_id)))
        return {"contract_version": CONTRACT_VERSION, "items": [public_assignment(e) for e in items]}

    def add_activity(self, context, lead_id, **data):
        return public_activity(self.service.add_activity(context, UUID(str(lead_id)), **data))

    def list_activities(self, context, lead_id):
        items = self.service.list_activities(context, UUID(str(lead_id)))
        return {"contract_version": CONTRACT_VERSION, "items": [public_activity(a) for a in items]}

    def link_person(self, context, lead_id, expected_version, person_id):
        return summary(self.service.link_person(context, UUID(str(lead_id)), expected_version, person_id))

    def find_duplicate_candidates(self, context, *, keys, limit=20):
        return self.service.find_duplicate_candidates(context, keys=keys, limit=limit)

    def add_external_reference(self, context, lead_id, **data):
        return public_external_reference(self.service.add_external_reference(context, UUID(str(lead_id)), **data))

    def list_external_references(self, context, lead_id):
        items = self.service.list_external_references(context, UUID(str(lead_id)))
        return {"contract_version": CONTRACT_VERSION, "items": [public_external_reference(r) for r in items]}

    def convert_lead(self, context, lead_id, **data):
        return public_external_reference(self.service.convert_lead(context, UUID(str(lead_id)), **data))

    def error(self, exc: Exception):
        return exc.to_json() if isinstance(exc, CrmError) else {"code": "INTERNAL_ERROR", "message": "CRM operation failed."}
