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
)

from services import (
    AuditLogService, 
    UserUpdateService
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
    This class provides a facade for user-related functionality.
    
    It uses various services to perform operations such as retrieving users, updating user data, etc.
    
    Attributes:
        session (AsyncSession): The current database session.
        
    Methods:
        get_by_id: Retrieves a user by their ID.
        search: Searches for users based on a query string.
        update_by_admin: Updates a user's data as an administrator.
        update_self: Updates a user's own data.
    """

    def __init__(
        self,
        session: AsyncSession,
        redis_cache: RedisCache,
    ):
        """
        Initializes the UserFacade instance.
        
        Args:
            session (AsyncSession): The current database session.
            redis_cache (RedisCache): The Redis cache instance.
            
        Returns:
            None
        """

        # Create an instance of the UserRepository class
        user_repository = UserRepository(
            session
        )

        # Create an instance of the RoleRepository class
        role_repository = RoleRepository(
            session
        )

        # Create an instance of the AuditLogRepository class
        audit_log_repository = (
            AuditLogRepository(
                session
            )
        )

        # Create an instance of the AuditLogService class
        audit_log_service = AuditLogService(
            audit_log_repository=(
                audit_log_repository
            ),
            redis_cache=redis_cache,
        )

        # Create instances of various utility classes
        normalizer = DataNormalizer()

        password_manager = PasswordManager()

        # Create an instance of the UserUpdateService class
        self.user_service = UserUpdateService(
            user_repository=user_repository,
            role_repository=role_repository,
            normalizer=normalizer,
            password_manager=password_manager,
            redis_cache=redis_cache,
        )

        # Set up audit log service for user service
        self.user_service.audit_log_service = (
            audit_log_service
        )

    # ==============================
    # Retrieve user by ID
    # ==============================

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse:
        """
        Retrieves a user by their ID.
        
        Args:
            user_id (int): The ID of the user to retrieve.
            
        Returns:
            UserResponse: The retrieved user response.
        """

        return await self.user_service.get_by_id(
            user_id
        )

    # ==============================
    # Search for users
    # ==============================

    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> UserListResponse:
        """
        Searches for users based on a query string.
        
        Args:
            query (str | None): The query string to search for users.
            page (int): The current page number.
            page_size (int): The size of each page.
            
        Returns:
            UserListResponse: The list of users matching the query.
        """

        return await self.user_service.search(
            query=query,
            page=page,
            page_size=page_size,
        )

    # ==============================
    # Update user data as administrator
    # ==============================

    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:
        """
        Updates a user's data as an administrator.
        
        Args:
            admin_id (int): The ID of the administrator updating the user.
            user_id (int): The ID of the user being updated.
            data (UserAdminUpdate): The new data for the user.
            
        Returns:
            UserResponse: The updated user response.
        """

        return await self.user_service.update_by_admin(
            admin_id=admin_id,
            user_id=user_id,
            data=data,
        )

    # ==============================
    # Update own data
    # ==============================

    async def update_self(
        self,
        user_id: int,
        data: UserSelfUpdate,
    ) -> UserResponse:
        """
        Updates a user's own data.
        
        Args:
            user_id (int): The ID of the user updating their own data.
            data (UserSelfUpdate): The new data for the user.
            
        Returns:
            UserResponse: The updated user response.
        """

        return await self.user_service.update_self(
            user_id=user_id,
            data=data,
        )