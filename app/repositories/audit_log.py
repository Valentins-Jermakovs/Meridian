# ==============================
# Repository Imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import (
    func, 
    select
)

from models import (
    AuditAction, 
    AuditLog
)


# ==============================
# Audit Log Repository
# ==============================

class AuditLogRepository:
    """
    A repository for audit log data storage and retrieval.
    
    Attributes:
        session (AsyncSession): The asynchronous database session.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        """
        Initializes the repository with an asynchronous database session.
        
        Args:
            session (AsyncSession): The asynchronous database session.
        """
        # Datu bāzes sesija
        self.session = session

    # Create a new audit log entry
    async def create(
        self,
        audit_log: AuditLog,
    ) -> AuditLog:
        """
        Creates a new audit log entry and adds it to the database.
        
        Args:
            audit_log (AuditLog): The audit log entry to be created.
        
        Returns:
            AuditLog: The newly created audit log entry.
        """
        self.session.add(
            audit_log
        )

        await self.session.flush()
        await self.session.refresh(
            audit_log
        )

        return audit_log

    # Search for audit logs
    async def search(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """
        Searches for audit logs based on the provided filters.
        
        Args:
            query (str | None): The search query to filter by description.
            user_id (int | None): The ID of the user to filter by.
            action (AuditAction | None): The action to filter by.
            success (bool | None): Whether the audit log was successful or not.
            page (int, optional): The current page number. Defaults to 1.
            page_size (int, optional): The number of results per page. Defaults to 20.
        
        Returns:
            tuple[list[AuditLog], int]: A tuple containing the list of audit logs and the total count.
        """
        offset = (
            page - 1
        ) * page_size

        statement = select(
            AuditLog
        )

        # Search by description
        if query:
            search_query = (
                f"%{query.strip()}%"
            )

            statement = statement.where(
                AuditLog.description.ilike(
                    search_query
                )
            )

        # Filter by user ID
        if user_id is not None:
            statement = statement.where(
                AuditLog.user_id == user_id
            )

        # Filter by action
        if action is not None:
            statement = statement.where(
                AuditLog.action == action
            )

        # Filter by success
        if success is not None:
            statement = statement.where(
                AuditLog.success == success
            )

        # Get the total count of audit logs
        count_statement = select(
            func.count()
        ).select_from(
            statement.subquery()
        )

        total_result = await self.session.execute(
            count_statement
        )

        total = total_result.scalar_one()

        # Get the results
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

    # Export audit logs
    async def export(
        self,
        query: str | None = None,
        user_id: int | None = None,
        action: AuditAction | None = None,
        success: bool | None = None,
    ) -> list[AuditLog]:
        """
        Exports all audit logs or filters them based on the provided parameters.
        
        Args:
            query (str | None): The search query to filter by description.
            user_id (int | None): The ID of the user to filter by.
            action (AuditAction | None): The action to filter by.
            success (bool | None): Whether the audit log was successful or not.
        
        Returns:
            list[AuditLog]: A list of all or filtered audit logs.
        """
        statement = select(
            AuditLog
        )

        # Search by description
        if query:
            search_query = (
                f"%{query.strip()}%"
            )

            statement = statement.where(
                AuditLog.description.ilike(
                    search_query
                )
            )

        # Filter by user ID
        if user_id is not None:
            statement = statement.where(
                AuditLog.user_id == user_id
            )

        # Filter by action
        if action is not None:
            statement = statement.where(
                AuditLog.action == action
            )

        # Filter by success
        if success is not None:
            statement = statement.where(
                AuditLog.success == success
            )

        # Order by created at in descending order
        statement = statement.order_by(
            AuditLog.created_at.desc()
        )

        result = await self.session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    # Get an audit log by ID
    async def get_by_id(
        self,
        audit_id: int,
    ) -> AuditLog | None:
        """
        Gets an audit log entry by its ID.
        
        Args:
            audit_id (int): The ID of the audit log entry.
        
        Returns:
            AuditLog | None: The audit log entry if found, otherwise None.
        """
        result = await self.session.execute(
            select(AuditLog).where(
                AuditLog.id == audit_id
            )
        )

        return result.scalar_one_or_none()

    # Commit changes to the database
    async def commit(self):
        """
        Commits the changes to the database.
        """
        await self.session.commit()

    # Rollback changes to the database
    async def rollback(self):
        """
        Rolls back the changes to the database.
        """
        await self.session.rollback()