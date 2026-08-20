# ==============================
# Bibliotēku imports
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

from schemas.audit import (
    AuditLogListItem,
    AuditLogListResponse,
)

from utils import RedisCache


# ==============================
# Audit žurnāla serviss
# ==============================

class AuditLogService:

    def __init__(
        self,
        audit_log_repository: AuditLogRepository,
        redis_cache: RedisCache,
    ):
        # Audit žurnāla repozitorijs
        self.audit_log_repository = (
            audit_log_repository
        )

        # Redis kešatmiņa
        self.redis_cache = redis_cache

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

        try:
            # Audit ieraksta izveide
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                description=description,
                success=success,
            )

            # Ieraksta saglabāšana
            audit_log = (
                await self.audit_log_repository.create(
                    audit_log
                )
            )

            # Izmaiņu saglabāšana
            await self.audit_log_repository.commit()

            return audit_log

        except Exception:

            # Izmaiņu atcelšana
            await self.audit_log_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to create audit log",
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

        # ==============================
        # Validācija
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
        # Normalizācija
        # ==============================

        if query is not None:
            query = query.strip()

            if not query:
                query = None

        # ==============================
        # Redis atslēga
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
        # Redis pārbaude
        # ==============================

        cached_result = await self.redis_cache.get(
            cache_key
        )

        if cached_result is not None:
            return AuditLogListResponse.model_validate(
                cached_result
            )

        # ==============================
        # PostgreSQL meklēšana
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
        # Atbildes elementu izveide
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
        # Kopējais lapu skaits
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
        # Redis saglabāšana
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
    # Audit žurnāla CSV eksports
    # ==============================

    async def export_csv(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
    ) -> bytes:

        # Meklēšanas teksta normalizācija
        if query is not None:

            query = query.strip()

            if not query:
                query = None

        try:
            # Ierakstu iegūšana pēc meklēšanas parametriem
            logs = (
                await self.audit_log_repository.export(
                    query=query,
                    user_id=user_id,
                    action=action,
                    success=success,
                )
            )

            # CSV izveide atmiņā
            output = io.StringIO(
                newline=""
            )

            writer = csv.writer(
                output,
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )

            # CSV galvene
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

            # Ierakstu pievienošana
            for log in logs:

                # CSV formula injection aizsardzība
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

            # UTF-8 BOM Excel saderībai
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