"""Máquina de estados y validaciones básicas del dominio (ADR-C06)."""
import pytest

from gi_crm.errors import InvalidTransitionError, ValidationError


def test_create_lead_starts_in_new(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Contacto web")
    assert lead.status == "new"
    assert lead.version == 1


def test_create_lead_rejects_blank_title(service, ctx_a):
    with pytest.raises(ValidationError):
        service.create_lead(ctx_a, title="   ")


@pytest.mark.parametrize(
    "sequence",
    [
        ["contacted", "qualified", "in_progress", "won"],
        ["contacted", "qualified", "in_progress", "lost"],
        ["archived"],
    ],
)
def test_valid_transition_sequences(service, ctx_a, sequence):
    lead = service.create_lead(ctx_a, title="Lead")
    version = lead.version
    for to_status in sequence:
        reason = "cerrado" if to_status in ("won", "lost") else None
        lead = service.change_status(ctx_a, lead.lead_id, version, to_status, reason=reason)
        version = lead.version
    assert lead.status == sequence[-1]


def test_invalid_transition_is_rejected(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    with pytest.raises(InvalidTransitionError):
        service.change_status(ctx_a, lead.lead_id, lead.version, "won")


@pytest.mark.parametrize("terminal", ["won", "lost", "archived"])
def test_terminal_statuses_have_no_outgoing_transition(service, ctx_a, terminal):
    lead = service.create_lead(ctx_a, title="Lead")
    lead = service.change_status(ctx_a, lead.lead_id, lead.version, "archived") \
        if terminal == "archived" else lead
    if terminal != "archived":
        lead = service.change_status(ctx_a, lead.lead_id, lead.version, "contacted")
        lead = service.change_status(ctx_a, lead.lead_id, lead.version, "qualified")
        lead = service.change_status(ctx_a, lead.lead_id, lead.version, "in_progress")
        lead = service.change_status(ctx_a, lead.lead_id, lead.version, terminal, reason="motivo")
    with pytest.raises(InvalidTransitionError):
        service.change_status(ctx_a, lead.lead_id, lead.version, "contacted")


def test_close_lead_requires_won_or_lost(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    with pytest.raises(ValidationError):
        service.close_lead(ctx_a, lead.lead_id, lead.version, "archived")


def test_add_activity_rejects_unknown_kind(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    with pytest.raises(ValidationError):
        service.add_activity(ctx_a, lead.lead_id, kind="carrier-pigeon")


def test_assign_lead_tracks_owner_and_history(service, ctx_a):
    lead = service.create_lead(ctx_a, title="Lead")
    updated = service.assign_lead(ctx_a, lead.lead_id, lead.version, "user-x")
    assert updated.owner_user_id == "user-x"
    history = service.list_assignments(ctx_a, lead.lead_id)
    assert len(history) == 1
    assert history[0].to_user_id == "user-x"
