# ==============================
# Library imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import (
    UserRepository,
    RoleRepository,
    AuditLogRepository,
)

from schemas import (
    UserAdminUpdate,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
    UserStatisticsResponse,
)

from services import (
    AuditLogService,
    UserUpdateService,
)

from utils import (
    DataNormalizer,
    PasswordManager,
    RedisCache,
)


# ==============================
# User Facade
# ==============================

class UserFacade:
    """
    Provides a simplified interface for user-related operations.

    The facade coordinates repositories, services, utilities,
    Redis caching, and audit logging.
    """

    def __init__(
        self,
        session: AsyncSession,
        redis_cache: RedisCache,
    ):
        """
        Initializes the UserFacade.

        Args:
            session (AsyncSession):
                Current asynchronous database session.
            redis_cache (RedisCache):
                Redis cache instance.
        """

        # ==============================
        # Repositories
        # ==============================

        user_repository = UserRepository(
            session
        )

        role_repository = RoleRepository(
            session
        )

        audit_log_repository = (
            AuditLogRepository(
                session
            )
        )

        # ==============================
        # Audit Log Service
        # ==============================

        audit_log_service = AuditLogService(
            audit_log_repository=(
                audit_log_repository
            ),
            redis_cache=redis_cache,
        )

        # ==============================
        # Utilities
        # ==============================

        normalizer = DataNormalizer()

        password_manager = PasswordManager()

        # ==============================
        # User Service
        # ==============================

        self.user_service = UserUpdateService(
            user_repository=user_repository,
            role_repository=role_repository,
            normalizer=normalizer,
            password_manager=password_manager,
            redis_cache=redis_cache,
        )

        # ==============================
        # Audit Service Injection
        # ==============================

        self.user_service.audit_log_service = (
            audit_log_service
        )

    # ==============================
    # Retrieve User by ID
    # ==============================

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse:
        """
        Retrieves a user by their ID.

        Args:
            user_id (int):
                ID of the requested user.

        Returns:
            UserResponse:
                Requested user information.
        """

        return await self.user_service.get_by_id(
            user_id
        )

    # ==============================
    # Search Users
    # ==============================

    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> UserListResponse:
        """
        Searches users with pagination.

        Args:
            query (str | None):
                Optional search query.
            page (int):
                Page number.
            page_size (int):
                Number of users per page.

        Returns:
            UserListResponse:
                Paginated user list.
        """

        return await self.user_service.search(
            query=query,
            page=page,
            page_size=page_size,
        )

    # ==============================
    # Update User as Administrator
    # ==============================

    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:
        """
        Updates a user's data using administrator privileges.

        Args:
            admin_id (int):
                Administrator ID.
            user_id (int):
                User ID being updated.
            data (UserAdminUpdate):
                User update data.

        Returns:
            UserResponse:
                Updated user information.
        """

        return await self.user_service.update_by_admin(
            admin_id=admin_id,
            user_id=user_id,
            data=data,
        )

    # ==============================
    # Update Own User Data
    # ==============================

    async def update_self(
        self,
        user_id: int,
        data: UserSelfUpdate,
    ) -> UserResponse:
        """
        Updates the authenticated user's own profile.

        Args:
            user_id (int):
                Authenticated user ID.
            data (UserSelfUpdate):
                User profile update data.

        Returns:
            UserResponse:
                Updated user information.
        """

        return await self.user_service.update_self(
            user_id=user_id,
            data=data,
        )

    # ==============================
    # Get User Statistics
    # ==============================

    async def get_statistics(
        self,
    ) -> UserStatisticsResponse:
        """
        Retrieves aggregated user statistics.

        Redis is used by the underlying service to cache
        the statistics and reduce repeated database queries.

        Returns:
            UserStatisticsResponse:
                Total, active, and blocked user counts.
        """

        return await self.user_service.get_statistics()