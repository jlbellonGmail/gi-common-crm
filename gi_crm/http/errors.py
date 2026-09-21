"""Mapeo de CrmError a status HTTP. Sin fuga de detalles internos."""
from ..errors import CrmError

_STATUS_BY_CODE = {
    "VALIDATION_ERROR": 400,
    "NOT_FOUND": 404,
    "FORBIDDEN": 403,
    "VERSION_CONFLICT": 409,
    "INVALID_TRANSITION": 409,
    "DUPLICATE_EXTERNAL_REFERENCE": 409,
    "CORE_UNAVAILABLE": 503,
    "UNSUPPORTED_CORE_CONTRACT": 503,
    "PERSONS_UNAVAILABLE": 503,
    "CAPABILITY_UNAVAILABLE": 501,
    "AUDIT_UNAVAILABLE": 500,
}


def status_for(exc: CrmError) -> int:
    return _STATUS_BY_CODE.get(exc.code, 500)
