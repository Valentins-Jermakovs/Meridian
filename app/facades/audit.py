# ==============================
# Library imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    AuditAction,
    AuditLog,
)

from repositories import AuditLogRepository

from schemas import AuditLogListResponse

from services import AuditLogService

from utils import RedisCache


# ==============================
# Audit Log Facade
# ==============================

class AuditLogFacade:
    """
    This class provides a facade for audit log-related functionality.
    
    It uses the AuditLogRepository and AuditLogService classes to 
    interact with the database and perform operations.
    
    Attributes:
        session (AsyncSession): The current database session.
        redis_cache (RedisCache): The Redis cache instance.
        
    Methods:
        create: Creates a new audit log entry.
        search: Searches for audit log entries based on various criteria.
        export_csv: Exports audit log entries to CSV format.
    """

    def __init__(
        self,
        session: AsyncSession,
        redis_cache: RedisCache,
    ):
        """
        Initializes the AuditLogFacade instance.
        
        Args:
            session (AsyncSession): The current database session.
            redis_cache (RedisCache): The Redis cache instance.
            
        Returns:
            None
        """

        # Create an instance of the AuditLogRepository class
        audit_log_repository = (
            AuditLogRepository(
                session
            )
        )

        # Create an instance of the AuditLogService class
        self.audit_log_service = (
            AuditLogService(
                audit_log_repository=(
                    audit_log_repository
                ),
                redis_cache=redis_cache,
            )
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
        """
        Creates a new audit log entry.
        
        Args:
            user_id (int | None): The ID of the user who performed the action. Defaults to None.
            action (AuditAction): The type of action that was performed.
            description (str): A brief description of the action.
            success (bool, optional): Whether the action was successful. Defaults to True.
            
        Returns:
            AuditLog: The created audit log entry.
        """
        
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
        """
        Searches for audit log entries based on various criteria.
        
        Args:
            query (str | None, optional): A search query to filter the results. Defaults to None.
            user_id (int | None, optional): The ID of the user who performed the action. Defaults to None.
            action (AuditAction | None, optional): The type of action that was performed. Defaults to None.
            success (bool | None, optional): Whether the action was successful. Defaults to None.
            page (int, optional): The current page number. Defaults to 1.
            page_size (int, optional): The number of results per page. Defaults to 20.
            
        Returns:
            AuditLogListResponse: A list of audit log entries matching the search criteria.
        """
        
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
        """
        Exports audit log entries to CSV format.
        
        Args:
            query (str | None, optional): A search query to filter the results. Defaults to None.
            user_id (int | None, optional): The ID of the user who performed the action. Defaults to None.
            action (AuditAction | None, optional): The type of action that was performed. Defaults to None.
            success (bool | None, optional): Whether the action was successful. Defaults to None.
            
        Returns:
            bytes: The exported CSV data as a bytes object.
        """
        
        return await self.audit_log_service.export_csv(
            query=query,
            user_id=user_id,
            action=action,
            success=success,
        )