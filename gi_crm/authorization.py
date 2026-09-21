"""Fail-closed CoreApi authorization boundary (ver ADR-C03)."""
from .errors import CoreUnavailableError, ForbiddenError, UnsupportedCoreContractError
from .models import RequestContext
from .ports import CoreApi

SUPPORTED_CORE_CONTRACT = "0.1.0"


class Authorizer:
    def __init__(self, api: CoreApi):
        self.api = api

    def require(self, context: RequestContext, permission: str) -> None:
        try:
            response = self.api.authorize(
                context.user_id, context.organization_id, permission, context.location_id
            )
        except Exception as exc:
            # CoreError concreto no se reemite: el llamador recibe una
            # categoría segura. Indisponibilidad nunca autoriza por
            # defecto (fail-safe).
            raise CoreUnavailableError() from exc
        if not isinstance(response, dict) or response.get("contract_version") != SUPPORTED_CORE_CONTRACT:
            raise UnsupportedCoreContractError()
        if response.get("allowed") is not True:
            raise ForbiddenError()
        returned = response.get("context")
        if (
            not isinstance(returned, dict)
            or returned.get("user_id") != context.user_id
            or returned.get("organization_id") != context.organization_id
        ):
            raise ForbiddenError()
