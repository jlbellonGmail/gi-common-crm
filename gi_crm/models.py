"""Domain values and trusted request context."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Estados terminales del ciclo de vida comercial del Lead: no admiten
# transición saliente. Ver ADR-C06 en docs/tecnica/arquitectura-crm.md.
TERMINAL_STATUSES = frozenset({"won", "lost", "archived"})

# Máquina de estados: new -> contacted -> qualified -> in_progress ->
# (won | lost); archived alcanzable desde cualquier estado no terminal.
VALID_TRANSITIONS: dict[str, frozenset[str]] = {
    "new": frozenset({"contacted", "archived"}),
    "contacted": frozenset({"qualified", "archived"}),
    "qualified": frozenset({"in_progress", "archived"}),
    "in_progress": frozenset({"won", "lost", "archived"}),
    "won": frozenset(),
    "lost": frozenset(),
    "archived": frozenset(),
}


@dataclass(frozen=True, slots=True)
class RequestContext:
    user_id: str
    tenant_id: str
    location_id: str | None = None
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    trusted: bool = True

    def __post_init__(self):
        if not self.trusted or not self.user_id or not self.tenant_id:
            raise ValueError("context must be trusted and identify user and tenant")


@dataclass(frozen=True, slots=True)
class LeadSource:
    source_id: UUID
    tenant_id: str
    code: str
    label: str
    active: bool = True
    created_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True, slots=True)
class Lead:
    lead_id: UUID
    tenant_id: str
    status: str = "new"
    person_id: UUID | None = None
    source_id: UUID | None = None
    owner_user_id: str | None = None
    title: str = ""
    description: str | None = None
    close_reason: str | None = None
    version: int = 1
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True, slots=True)
class LeadStatusEvent:
    event_id: UUID
    tenant_id: str
    lead_id: UUID
    from_status: str | None
    to_status: str
    actor_user_id: str
    occurred_at: datetime = field(default_factory=utcnow)
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class LeadActivity:
    activity_id: UUID
    tenant_id: str
    lead_id: UUID
    actor_user_id: str
    kind: str
    notes: str = ""
    occurred_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True, slots=True)
class LeadAssignmentEvent:
    assignment_id: UUID
    tenant_id: str
    lead_id: UUID
    from_user_id: str | None
    to_user_id: str
    actor_user_id: str
    occurred_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True, slots=True)
class LeadExternalReference:
    reference_id: UUID
    tenant_id: str
    lead_id: UUID
    vertical_code: str
    external_type: str
    external_id: str
    created_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True, slots=True)
class LeadAudit:
    audit_id: UUID
    tenant_id: str
    lead_id: UUID | None
    actor_user_id: str
    action: str
    occurred_at: datetime
    correlation_id: str
    outcome: str
    entity_version: int | None


def json_value(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    return value
