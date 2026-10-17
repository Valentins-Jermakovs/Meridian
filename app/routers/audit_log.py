
# ==============================
# Standard library imports
# ==============================

from typing import Annotated

# ==============================
# Third-party imports
# ==============================

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

# ==============================
# Application facades
# ==============================

from facades import AuditLogFacade

# ==============================
# Application models
# ==============================

from models import AuditAction

# ==============================
# Application schemas
# ==============================

from schemas import AuditLogListResponse

# ==============================
# Router dependencies
# ==============================

from routers.dependencies import (
    get_audit_log_facade,
    jwt_auth,
)


# ==============================
# Audit log router
# ==============================

router = APIRouter(
    prefix="/audit",
    tags=["Audit log"],
)


# ==============================
# Search audit logs
# Administrator only
# ==============================

@router.get(
    "/",
    response_model=AuditLogListResponse,
)
async def search_audit_logs(
    current_user: Annotated[
        dict,
        Depends(jwt_auth.require_roles(["admin"])),
    ],
    facade: Annotated[
        AuditLogFacade,
        Depends(get_audit_log_facade),
    ],
    query: str | None = Query(default=None),
    user_id: int | None = Query(default=None, ge=1),
    action: AuditAction | None = Query(default=None),
    success: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> AuditLogListResponse:
    """Search audit logs using the requested filters."""
    return await facade.search(
        query=query,
        user_id=user_id,
        action=action,
        success=success,
        page=page,
        page_size=page_size,
    )


# ==============================
# Export audit logs
# Administrator only
# ==============================

@router.get("/export")
async def export_audit_logs(
    current_user: Annotated[
        dict,
        Depends(jwt_auth.require_roles(["admin"])),
    ],
    facade: Annotated[
        AuditLogFacade,
        Depends(get_audit_log_facade),
    ],
    query: str | None = Query(default=None),
    user_id: int | None = Query(default=None, ge=1),
    action: AuditAction | None = Query(default=None),
    success: bool | None = Query(default=None),
) -> Response:
    """Export filtered audit logs as a CSV file."""
    csv_data = await facade.export_csv(
        query=query,
        user_id=user_id,
        action=action,
        success=success,
    )

    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                'attachment; filename="audit_log.csv"'
            ),
        },
    )
