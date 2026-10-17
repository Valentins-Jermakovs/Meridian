
# ==============================
# Third-party imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

# ==============================
# Application models
# ==============================

from models import AuditAction, AuditLog

# ==============================
# Application repositories
# ==============================

from repositories import AuditLogRepository

# ==============================
# Application schemas
# ==============================

from schemas import AuditLogListResponse

# ==============================
# Application services
# ==============================

from services import AuditLogService


# ==============================
# Audit log facade
# ==============================

class AuditLogFacade:
    """Provide a unified interface for audit log operations."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """Initialize the audit log facade."""

        # Initialize the repository.
        audit_log_repository = AuditLogRepository(session)

        # Initialize the service using the centralized Redis cache.
        self.audit_log_service = AuditLogService(
            audit_log_repository=audit_log_repository,
        )

    # ==============================
    # Create audit log entry
    # ==============================

    async def create(
        self,
        user_id: int | None,
        action: AuditAction,
        description: str,
        success: bool = True,
    ) -> AuditLog:
        """Create a new audit log entry."""
        return await self.audit_log_service.create(
            user_id=user_id,
            action=action,
            description=description,
            success=success,
        )

    # ==============================
    # Search audit log entries
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
        """Search audit log entries with pagination."""
        return await self.audit_log_service.search(
            query=query,
            user_id=user_id,
            action=action,
            success=success,
            page=page,
            page_size=page_size,
        )

    # ==============================
    # Export audit log to CSV
    # ==============================

    async def export_csv(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
    ) -> bytes:
        """Export filtered audit log entries as CSV."""
        return await self.audit_log_service.export_csv(
            query=query,
            user_id=user_id,
            action=action,
            success=success,
        )
