
# ==============================
# Third-party imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

# ==============================
# Application repositories
# ==============================

from repositories import (
    AuditLogRepository,
    RoleRepository,
    UserRepository,
)

# ==============================
# Application schemas
# ==============================

from schemas import (
    UserAdminUpdate,
    UserListResponse,
    UserRegistrationStatisticsResponse,
    UserResponse,
    UserSelfUpdate,
    UserStatisticsResponse,
)

# ==============================
# Application services
# ==============================

from services import (
    AuditLogService,
    UserUpdateService,
)

# ==============================
# Application utilities
# ==============================

from utils import (
    DataNormalizer,
    PasswordManager,
)


# ==============================
# User facade
# ==============================

class UserFacade:
    """Coordinate user services, repositories, and audit logging."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """Initialize the user facade."""

        # ==============================
        # Repositories
        # ==============================

        user_repository = UserRepository(session)
        role_repository = RoleRepository(session)
        audit_log_repository = AuditLogRepository(session)

        # ==============================
        # Audit log service
        # ==============================

        audit_log_service = AuditLogService(
            audit_log_repository=audit_log_repository,
        )

        # ==============================
        # Utilities
        # ==============================

        normalizer = DataNormalizer()
        password_manager = PasswordManager()

        # ==============================
        # User service
        # ==============================

        self.user_service = UserUpdateService(
            user_repository=user_repository,
            role_repository=role_repository,
            normalizer=normalizer,
            password_manager=password_manager,
        )

        # ==============================
        # Audit service injection
        # ==============================

        self.user_service.audit_log_service = audit_log_service

    # ==============================
    # Retrieve user by ID
    # ==============================

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse:
        """Retrieve a user by their ID."""
        return await self.user_service.get_by_id(user_id)

    # ==============================
    # Search users
    # ==============================

    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> UserListResponse:
        """Search users with pagination."""
        return await self.user_service.search(
            query=query,
            page=page,
            page_size=page_size,
        )

    # ==============================
    # Update user as administrator
    # ==============================

    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:
        """Update a user's data using administrator privileges."""
        return await self.user_service.update_by_admin(
            admin_id=admin_id,
            user_id=user_id,
            data=data,
        )

    # ==============================
    # Update own user data
    # ==============================

    async def update_self(
        self,
        user_id: int,
        data: UserSelfUpdate,
    ) -> UserResponse:
        """Update the authenticated user's own profile."""
        return await self.user_service.update_self(
            user_id=user_id,
            data=data,
        )

    # ==============================
    # Get user statistics
    # ==============================

    async def get_statistics(self) -> UserStatisticsResponse:
        """Retrieve aggregated user statistics."""
        return await self.user_service.get_statistics()

    # ==============================
    # Get user registration statistics
    # ==============================

    async def get_registration_statistics(
        self,
        year: int | None = None,
    ) -> UserRegistrationStatisticsResponse:
        """Retrieve monthly user registration statistics."""
        return await self.user_service.get_registration_statistics(
            year=year,
        )
