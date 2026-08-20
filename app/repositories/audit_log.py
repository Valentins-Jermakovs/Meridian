# ==============================
# Bibliotēku imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from models import AuditAction, AuditLog


# ==============================
# Audit žurnāla repozitorijs
# ==============================

class AuditLogRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        # Datu bāzes sesija
        self.session = session

    # Audit ieraksta izveide
    async def create(
        self,
        audit_log: AuditLog,
    ) -> AuditLog:

        self.session.add(
            audit_log
        )

        await self.session.flush()
        await self.session.refresh(
            audit_log
        )

        return audit_log

    # Audit žurnāla meklēšana
    async def search(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:

        offset = (
            page - 1
        ) * page_size

        statement = select(
            AuditLog
        )

        # Meklēšana pēc apraksta
        if query:
            search_query = (
                f"%{query.strip()}%"
            )

            statement = statement.where(
                AuditLog.description.ilike(
                    search_query
                )
            )

        # Filtrs pēc lietotāja
        if user_id is not None:
            statement = statement.where(
                AuditLog.user_id == user_id
            )

        # Filtrs pēc darbības
        if action is not None:
            statement = statement.where(
                AuditLog.action == action
            )

        # Filtrs pēc rezultāta
        if success is not None:
            statement = statement.where(
                AuditLog.success == success
            )

        # Kopējais ierakstu skaits
        count_statement = select(
            func.count()
        ).select_from(
            statement.subquery()
        )

        total_result = await self.session.execute(
            count_statement
        )

        total = total_result.scalar_one()

        # Rezultātu iegūšana
        statement = (
            statement
            .order_by(
                AuditLog.created_at.desc()
            )
            .offset(offset)
            .limit(page_size)
        )

        result = await self.session.execute(
            statement
        )

        logs = list(
            result.scalars().all()
        )

        return logs, total

    # Audit žurnāla eksports
    async def export(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
    ) -> list[AuditLog]:

        statement = select(
            AuditLog
        )

        # Meklēšana pēc apraksta
        if query:
            search_query = (
                f"%{query.strip()}%"
            )

            statement = statement.where(
                AuditLog.description.ilike(
                    search_query
                )
            )

        # Filtrs pēc lietotāja
        if user_id is not None:
            statement = statement.where(
                AuditLog.user_id == user_id
            )

        # Filtrs pēc darbības
        if action is not None:
            statement = statement.where(
                AuditLog.action == action
            )

        # Filtrs pēc rezultāta
        if success is not None:
            statement = statement.where(
                AuditLog.success == success
            )

        # Jaunākie ieraksti vispirms
        statement = statement.order_by(
            AuditLog.created_at.desc()
        )

        result = await self.session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    # Audit ieraksta meklēšana pēc ID
    async def get_by_id(
        self,
        audit_id: int,
    ) -> AuditLog | None:

        result = await self.session.execute(
            select(AuditLog).where(
                AuditLog.id == audit_id
            )
        )

        return result.scalar_one_or_none()

    # Izmaiņu saglabāšana
    async def commit(self):
        await self.session.commit()

    # Izmaiņu atcelšana
    async def rollback(self):
        await self.session.rollback()