# ==============================
# Bibliotēku imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    AuditAction,
    AuditLog,
)

from repositories import AuditLogRepository

from schemas.audit import (
    AuditLogListResponse,
)

from services import AuditLogService

from utils import RedisCache


# ==============================
# Audit žurnāla fasāde
# ==============================

class AuditLogFacade:

    def __init__(
        self,
        session: AsyncSession,
        redis_cache: RedisCache,
    ):
        # Audit žurnāla repozitorijs
        audit_log_repository = (
            AuditLogRepository(
                session
            )
        )

        # Audit žurnāla serviss
        self.audit_log_service = (
            AuditLogService(
                audit_log_repository=(
                    audit_log_repository
                ),
                redis_cache=redis_cache,
            )
        )

    # ==============================
    # Audit ieraksta izveide
    # ==============================

    async def create(
        self,
        user_id: int | None,
        action: AuditAction,
        description: str,
        success: bool = True,
    ) -> AuditLog:

        return await self.audit_log_service.create(
            user_id=user_id,
            action=action,
            description=description,
            success=success,
        )

    # ==============================
    # Audit žurnāla meklēšana
    # ==============================

    async def search(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AuditLogListResponse:

        return await self.audit_log_service.search(
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

    async def export_csv(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
    ) -> bytes:

        return await self.audit_log_service.export_csv(
            query=query,
            user_id=user_id,
            action=action,
            success=success,
        )