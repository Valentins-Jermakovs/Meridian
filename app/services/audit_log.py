# ==============================
# Library Imports
# ==============================

import csv
import io
from math import ceil

from fastapi import HTTPException

from models import (
    AuditAction,
    AuditLog,
)

from repositories import AuditLogRepository

from schemas import (
    AuditLogListItem,
    AuditLogListResponse,
)

from utils import RedisCache


# ==============================
# Audit Log Service
# ==============================

class AuditLogService:
    """
    Provides business logic for creating, searching, caching,
    and exporting audit log entries.
    """


    def __init__(
        self,
        audit_log_repository: AuditLogRepository,
        redis_cache: RedisCache,
    ):
        """
        Initializes the audit log service.

        Args:
            audit_log_repository (AuditLogRepository):
                Repository used to access audit log data.
            redis_cache (RedisCache):
                Redis cache used to store temporary search results.
        """

        # Audit log repository
        self.audit_log_repository = (
            audit_log_repository
        )

        # Redis cache
        self.redis_cache = redis_cache


    # ==============================
    # Create Audit Log Entry
    # ==============================

    async def create(
        self,
        user_id: int | None,
        action: AuditAction,
        description: str,
        success: bool = True,
    ) -> AuditLog:
        """
        Creates and saves a new audit log entry.

        Args:
            user_id (int | None): Identifier of the user who performed the action.
            action (AuditAction): Type of action that was performed.
            description (str): Description of the performed action.
            success (bool): Indicates whether the action was successful.

        Returns:
            AuditLog: The newly created audit log entry.

        Raises:
            HTTPException: If the audit log cannot be created.
        """

        try:
            # Create a new audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                description=description,
                success=success,
            )

            # Save the audit log entry
            audit_log = (
                await self.audit_log_repository.create(
                    audit_log
                )
            )

            # Commit the changes
            await self.audit_log_repository.commit()

            return audit_log

        except Exception:

            # Roll back the transaction
            await self.audit_log_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to create audit log",
            )


    # ==============================
    # Search Audit Logs
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
        Searches audit log entries using the specified filters.

        Search results are cached in Redis for a short period
        to reduce repeated database queries.

        Args:
            query (str | None): Text used to search audit log descriptions.
            user_id (int | None): Filter by user identifier.
            action (AuditAction | None): Filter by action type.
            success (bool | None): Filter by operation success status.
            page (int): Page number to return.
            page_size (int): Number of entries per page.

        Returns:
            AuditLogListResponse: Paginated audit log search results.

        Raises:
            HTTPException: If the page or page size is invalid.
        """

        # ==============================
        # Validation
        # ==============================

        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="Page must be greater than 0",
            )

        if page_size < 1:
            raise HTTPException(
                status_code=400,
                detail="Page size must be greater than 0",
            )

        if page_size > 100:
            raise HTTPException(
                status_code=400,
                detail="Page size cannot exceed 100",
            )

        # ==============================
        # Normalization
        # ==============================

        if query is not None:
            query = query.strip()

            if not query:
                query = None

        # ==============================
        # Generate Redis Cache Key
        # ==============================

        cache_key = (
            "audit:search:"
            f"{query or 'all'}:"
            f"{user_id if user_id is not None else 'all'}:"
            f"{action.value if action else 'all'}:"
            f"{'true' if success is True else 'false' if success is False else 'all'}:"
            f"{page}:"
            f"{page_size}"
        )

        # ==============================
        # Check Redis Cache
        # ==============================

        cached_result = await self.redis_cache.get(
            cache_key
        )

        if cached_result is not None:
            return AuditLogListResponse.model_validate(
                cached_result
            )

        # ==============================
        # Search PostgreSQL
        # ==============================

        logs, total = (
            await self.audit_log_repository.search(
                query=query,
                user_id=user_id,
                action=action,
                success=success,
                page=page,
                page_size=page_size,
            )
        )

        # ==============================
        # Create Response Items
        # ==============================

        items = [
            AuditLogListItem(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                description=log.description,
                success=log.success,
                created_at=log.created_at,
            )
            for log in logs
            if log.id is not None
        ]

        # ==============================
        # Calculate Total Pages
        # ==============================

        pages = ceil(
            total / page_size
        )

        response = AuditLogListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            pages=pages,
        )

        # ==============================
        # Store Result in Redis
        # ==============================

        await self.redis_cache.set(
            cache_key,
            response.model_dump(
                mode="json"
            ),
            ttl=5,
        )

        return response


    # ==============================
    # Export Audit Logs to CSV
    # ==============================

    async def export_csv(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
    ) -> bytes:
        """
        Exports filtered audit log entries as a CSV file.

        The CSV file is generated in memory and returned as UTF-8
        encoded bytes. Formula injection protection is applied to
        description values before writing them to the CSV file.

        Args:
            query (str | None): Text used to search audit log descriptions.
            user_id (int | None): Filter by user identifier.
            action (AuditAction | None): Filter by action type.
            success (bool | None): Filter by operation success status.

        Returns:
            bytes: UTF-8 encoded CSV data with a BOM for Excel compatibility.

        Raises:
            HTTPException: If the audit log export fails.
        """

        # Normalize the search query
        if query is not None:

            query = query.strip()

            if not query:
                query = None

        try:
            # Retrieve audit log entries using the specified filters
            logs = (
                await self.audit_log_repository.export(
                    query=query,
                    user_id=user_id,
                    action=action,
                    success=success,
                )
            )

            # Create the CSV file in memory
            output = io.StringIO(
                newline=""
            )

            writer = csv.writer(
                output,
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )

            # Write the CSV header
            writer.writerow(
                [
                    "ID",
                    "User ID",
                    "Action",
                    "Description",
                    "Success",
                    "Created At",
                ]
            )

            # Write audit log entries
            for log in logs:

                # Protect against CSV formula injection
                description = (
                    log.description
                )

                if description.startswith(
                    ("=", "+", "-", "@")
                ):
                    description = (
                        "'"
                        + description
                    )

                writer.writerow(
                    [
                        log.id,
                        log.user_id,
                        log.action.value,
                        description,
                        str(
                            log.success
                        ).lower(),
                        log.created_at.isoformat(
                            sep=" "
                        ),
                    ]
                )

            # Add UTF-8 BOM for Excel compatibility
            return (
                "\ufeff"
                + output.getvalue()
            ).encode(
                "utf-8"
            )

        except Exception:

            raise HTTPException(
                status_code=500,
                detail="Failed to export audit log",
            )