"""Public, transport-neutral CRM errors."""


class CrmError(Exception):
    code = "CRM_ERROR"
    safe_message = "CRM operation failed."

    def __init__(self, message: str | None = None, *, details: dict | None = None):
        super().__init__(message or self.safe_message)
        self.details = details or {}

    def to_json(self) -> dict:
        return {"code": self.code, "message": self.safe_message}


class ValidationError(CrmError):
    code = "VALIDATION_ERROR"
    safe_message = "The request is invalid."


class NotFoundError(CrmError):
    code = "NOT_FOUND"
    safe_message = "The requested resource was not found."


class ForbiddenError(CrmError):
    code = "FORBIDDEN"
    safe_message = "The operation is not permitted."


class VersionConflictError(CrmError):
    code = "VERSION_CONFLICT"
    safe_message = "The resource changed; refresh and retry."


class InvalidTransitionError(CrmError):
    code = "INVALID_TRANSITION"
    safe_message = "The requested status transition is not allowed."


class DuplicateExternalReferenceError(CrmError):
    code = "DUPLICATE_EXTERNAL_REFERENCE"
    safe_message = "The external reference already exists for this organization and vertical."


class CoreUnavailableError(CrmError):
    code = "CORE_UNAVAILABLE"
    safe_message = "Authorization provider unavailable."


class UnsupportedCoreContractError(CrmError):
    code = "UNSUPPORTED_CORE_CONTRACT"
    safe_message = "Authorization contract unsupported."


class PersonsUnavailableError(CrmError):
    code = "PERSONS_UNAVAILABLE"
    safe_message = "Persons provider unavailable."


class CapabilityUnavailableError(CrmError):
    code = "CAPABILITY_UNAVAILABLE"
    safe_message = "This capability is not available."


class AuditFailureError(CrmError):
    code = "AUDIT_UNAVAILABLE"
    safe_message = "The operation could not be safely recorded."
