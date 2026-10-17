
# ==============================
# Standard library imports
# ==============================

import csv
import io
from math import ceil

# ==============================
# Third-party imports
# ==============================

from fastapi import HTTPException

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

from schemas import (
    AuditLogListItem,
    AuditLogListResponse,
)

# ==============================
# Application configuration
# ==============================

from config.redis import get_redis_cache


# ==============================
# Audit log service
# ==============================

class AuditLogService:
    """Create, search, cache, and export audit log entries."""

    def __init__(
        self,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        """Initialize the audit log service."""
        self.audit_log_repository = audit_log_repository

        # Use the shared Redis cache.
        self.redis_cache = get_redis_cache()

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
        """Create and save an audit log entry."""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                description=description,
                success=success,
            )

            audit_log = await self.audit_log_repository.create(
                audit_log
            )

            await self.audit_log_repository.commit()

            return audit_log

        except Exception:
            await self.audit_log_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to create audit log",
            ) from None

    # ==============================
    # Search audit logs
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
        """Search audit logs with pagination and Redis caching."""

        # Validate pagination parameters.
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

        # Normalize the search query.
        if query is not None:
            query = query.strip()

            if not query:
                query = None

        # Build a cache key from the search parameters.
        cache_key = (
            "audit:search:"
            f"{query or 'all'}:"
            f"{user_id if user_id is not None else 'all'}:"
            f"{action.value if action else 'all'}:"
            f"{'true' if success is True else 'false' if success is False else 'all'}:"
            f"{page}:"
            f"{page_size}"
        )

        # Return cached results when available.
        cached_result = await self.redis_cache.get(cache_key)

        if cached_result is not None:
            return AuditLogListResponse.model_validate(
                cached_result
            )

        # Query PostgreSQL.
        logs, total = await self.audit_log_repository.search(
            query=query,
            user_id=user_id,
            action=action,
            success=success,
            page=page,
            page_size=page_size,
        )

        # Convert database records into response items.
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

        response = AuditLogListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            pages=ceil(total / page_size),
        )

        # Cache search results briefly.
        await self.redis_cache.set(
            cache_key,
            response.model_dump(mode="json"),
            ttl=5,
        )

        return response

    # ==============================
    # Export audit logs
    # ==============================

    async def export_csv(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
    ) -> bytes:
        """Export filtered audit logs as a UTF-8 CSV file."""
        if query is not None:
            query = query.strip()

            if not query:
                query = None

        try:
            # Retrieve matching audit log entries.
            logs = await self.audit_log_repository.export(
                query=query,
                user_id=user_id,
                action=action,
                success=success,
            )

            # Build the CSV file in memory.
            output = io.StringIO(newline="")

            writer = csv.writer(
                output,
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )

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

            # Write rows and protect against CSV formula injection.
            for log in logs:
                description = log.description

                if description.startswith(("=", "+", "-", "@")):
                    description = "'" + description

                writer.writerow(
                    [
                        log.id,
                        log.user_id,
                        log.action.value,
                        description,
                        str(log.success).lower(),
                        log.created_at.isoformat(sep=" "),
                    ]
                )

            # Add a UTF-8 BOM for spreadsheet compatibility.
            csv_content = "\ufeff" + output.getvalue()

            return csv_content.encode("utf-8")

        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to export audit log",
            ) from None
