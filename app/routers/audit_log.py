# ==============================
# Bibliotēku imports
# ==============================

from fastapi import (
    APIRouter,
    Depends,
)

from fastapi.responses import Response

from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from config.database import get_session
from config.redis import redis_client

from facades.audit import AuditLogFacade

from models import AuditAction

from schemas.audit import (
    AuditLogListResponse,
)

from utils import (
    JWTManager,
    JWTAuth,
    RedisCache,
)


# ==============================
# JWT konfigurācija
# ==============================

jwt_manager = JWTManager(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
    access_token_expire_minutes=(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
    ),
)

jwt_auth = JWTAuth(
    jwt_manager=jwt_manager,
)


# ==============================
# Redis konfigurācija
# ==============================

redis_cache = RedisCache(
    client=redis_client,
    ttl=settings.REDIS_CACHE_TTL,
)


# ==============================
# Audit žurnāla maršrutētājs
# ==============================

router = APIRouter(
    prefix="/audit",
    tags=["Audit log"],
)


# ==============================
# Audit žurnāla meklēšana
# ==============================

@router.get(
    "/",
    response_model=AuditLogListResponse,
)
async def search_audit_logs(
    query: str | None = None,
    user_id: int | None = None,
    action: AuditAction | None = None,
    success: bool | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(
        jwt_auth.require_roles(
            ["admin"]
        )
    ),
    session: AsyncSession = Depends(
        get_session
    ),
):
    facade = AuditLogFacade(
        session=session,
        redis_cache=redis_cache,
    )

    return await facade.search(
        query=query,
        user_id=user_id,
        action=action,
        success=success,
        page=page,
        page_size=page_size,
    )


# ==============================
# Audit žurnāla CSV eksports
# ==============================

@router.get(
    "/export",
)
async def export_audit_logs(
    query: str | None = None,
    user_id: int | None = None,
    action: AuditAction | None = None,
    success: bool | None = None,
    current_user: dict = Depends(
        jwt_auth.require_roles(
            ["admin"]
        )
    ),
    session: AsyncSession = Depends(
        get_session
    ),
):
    facade = AuditLogFacade(
        session=session,
        redis_cache=redis_cache,
    )

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