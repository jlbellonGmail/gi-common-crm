"""API HTTP versionada de gi_crm (extra `[http]`).

Contexto de tenant por cabeceras confiables (`X-GI-User-Id`,
`X-GI-Tenant-Id`, `X-GI-Location-Id`) inyectadas por el host/proxy
autenticado -- mismo supuesto interino que `RequestContext(trusted=True)`
en la biblioteca (ver ADR-C05/ADR-C03 en docs/tecnica/arquitectura-crm.md).
Esta app no reimplementa reglas de negocio: delega íntegramente en
`gi_crm.api.LeadsApi`, para que biblioteca y HTTP den la misma respuesta
funcional ante la misma operación.
"""
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from ..errors import CrmError
from ..models import RequestContext
from .errors import status_for
from .schemas import (
    AddActivityRequest,
    AssignRequest,
    ChangeStatusRequest,
    CloseLeadRequest,
    CreateLeadRequest,
    ExternalReferenceRequest,
    LinkPersonRequest,
    UpdateLeadRequest,
)


def create_app(leads_api) -> FastAPI:
    app = FastAPI(title="GI-COMMON-CRM", version="0.1.0")

    def get_context(
        x_gi_user_id: str | None = Header(None),
        x_gi_tenant_id: str | None = Header(None),
        x_gi_location_id: str | None = Header(None),
    ) -> RequestContext:
        # Cabeceras opcionales a nivel de FastAPI para que la falta de
        # contexto confiable se traduzca siempre en 400 (RequestContext
        # fail-safe), no en el 422 genérico de validación de Pydantic.
        try:
            return RequestContext(
                user_id=x_gi_user_id, tenant_id=x_gi_tenant_id, location_id=x_gi_location_id,
            )
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail="missing trusted context headers") from exc

    @app.exception_handler(CrmError)
    def handle_crm_error(request, exc: CrmError):
        return JSONResponse(status_code=status_for(exc), content=leads_api.error(exc))

    @app.post("/v1/leads", status_code=201)
    def create_lead(payload: CreateLeadRequest, context: RequestContext = Depends(get_context)):
        return leads_api.create_lead(context, **payload.model_dump(exclude_unset=True))

    @app.get("/v1/leads/{lead_id}")
    def get_lead(lead_id: str, context: RequestContext = Depends(get_context)):
        return leads_api.get_lead(context, lead_id)

    @app.get("/v1/leads")
    def list_leads(limit: int = 20, cursor: str | None = None, context: RequestContext = Depends(get_context)):
        return leads_api.list_leads(context, limit=limit, cursor=cursor)

    @app.patch("/v1/leads/{lead_id}")
    def update_lead(lead_id: str, payload: UpdateLeadRequest, context: RequestContext = Depends(get_context)):
        fields = payload.model_dump(exclude_unset=True, exclude={"expected_version"})
        return leads_api.update_lead(context, lead_id, payload.expected_version, **fields)

    @app.post("/v1/leads/{lead_id}/status")
    def change_status(lead_id: str, payload: ChangeStatusRequest, context: RequestContext = Depends(get_context)):
        return leads_api.change_status(context, lead_id, payload.expected_version, payload.to_status, reason=payload.reason)

    @app.post("/v1/leads/{lead_id}/close")
    def close_lead(lead_id: str, payload: CloseLeadRequest, context: RequestContext = Depends(get_context)):
        return leads_api.close_lead(context, lead_id, payload.expected_version, payload.outcome, reason=payload.reason)

    @app.get("/v1/leads/{lead_id}/status-history")
    def list_status_history(lead_id: str, context: RequestContext = Depends(get_context)):
        return leads_api.list_status_history(context, lead_id)

    @app.post("/v1/leads/{lead_id}/assign")
    def assign_lead(lead_id: str, payload: AssignRequest, context: RequestContext = Depends(get_context)):
        return leads_api.assign_lead(context, lead_id, payload.expected_version, payload.to_user_id)

    @app.get("/v1/leads/{lead_id}/assignments")
    def list_assignments(lead_id: str, context: RequestContext = Depends(get_context)):
        return leads_api.list_assignments(context, lead_id)

    @app.post("/v1/leads/{lead_id}/activities", status_code=201)
    def add_activity(lead_id: str, payload: AddActivityRequest, context: RequestContext = Depends(get_context)):
        return leads_api.add_activity(context, lead_id, kind=payload.kind, notes=payload.notes)

    @app.get("/v1/leads/{lead_id}/activities")
    def list_activities(lead_id: str, context: RequestContext = Depends(get_context)):
        return leads_api.list_activities(context, lead_id)

    @app.post("/v1/leads/{lead_id}/link-person")
    def link_person(lead_id: str, payload: LinkPersonRequest, context: RequestContext = Depends(get_context)):
        return leads_api.link_person(context, lead_id, payload.expected_version, payload.person_id)

    @app.post("/v1/leads/{lead_id}/external-references", status_code=201)
    def add_external_reference(lead_id: str, payload: ExternalReferenceRequest, context: RequestContext = Depends(get_context)):
        return leads_api.add_external_reference(context, lead_id, **payload.model_dump())

    @app.get("/v1/leads/{lead_id}/external-references")
    def list_external_references(lead_id: str, context: RequestContext = Depends(get_context)):
        return leads_api.list_external_references(context, lead_id)

    @app.post("/v1/leads/{lead_id}/convert", status_code=201)
    def convert_lead(lead_id: str, payload: ExternalReferenceRequest, context: RequestContext = Depends(get_context)):
        return leads_api.convert_lead(context, lead_id, **payload.model_dump())

    return app
