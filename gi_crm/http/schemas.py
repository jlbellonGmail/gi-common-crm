"""Modelos Pydantic de request/response. Requiere el extra `[http]`."""
from pydantic import BaseModel


class CreateLeadRequest(BaseModel):
    title: str
    description: str | None = None
    person_id: str | None = None
    source_id: str | None = None
    owner_user_id: str | None = None


class UpdateLeadRequest(BaseModel):
    expected_version: int
    title: str | None = None
    description: str | None = None
    source_id: str | None = None
    person_id: str | None = None


class ChangeStatusRequest(BaseModel):
    expected_version: int
    to_status: str
    reason: str | None = None


class CloseLeadRequest(BaseModel):
    expected_version: int
    outcome: str
    reason: str | None = None


class AssignRequest(BaseModel):
    expected_version: int
    to_user_id: str


class AddActivityRequest(BaseModel):
    kind: str
    notes: str = ""


class LinkPersonRequest(BaseModel):
    expected_version: int
    person_id: str


class ExternalReferenceRequest(BaseModel):
    vertical_code: str
    external_type: str
    external_id: str
