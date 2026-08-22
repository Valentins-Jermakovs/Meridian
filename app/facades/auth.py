# ==============================
# Library imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from config.redis import redis_client

from repositories import (
    UserRepository,
    RoleRepository,
    RefreshTokenRepository,
    AuditLogRepository,
)

from schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    TokenCleanupResponse
)

from services import (
    AuditLogService,
    LoginService,
    LogoutService,
    RefreshTokenService,
    RegistrationService,
    TokenCleanupService,
)

from utils import (
    DataNormalizer,
    PasswordManager,
    JWTManager,
    RefreshTokenManager,
    RedisCache,
)


# ==============================
# Authentication Facade
# ==============================

class AuthFacade:
    """
    This class provides a facade for authentication-related functionality.
    
    It uses various services to perform operations such as registration, 
    login, and logout.
    
    Attributes:
        session (AsyncSession): The current database session.
        
    Methods:
        register: Registers a new user.
        login: Logs in an existing user.
        refresh: Rotates the refresh token for the current user.
        logout: Logs out the current user from their current session.
        logout_all: Logs out all sessions for a given user ID.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        """
        Initializes the AuthFacade instance.
        
        Args:
            session (AsyncSession): The current database session.
            
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

        # Create an instance of the RefreshTokenRepository class
        refresh_token_repository = (
            RefreshTokenRepository(
                session
            )
        )

        # Create an instance of the AuditLogRepository class
        audit_log_repository = (
            AuditLogRepository(
                session
            )
        )

        # Create a Redis cache instance
        redis_cache = RedisCache(
            client=redis_client,
            ttl=settings.REDIS_CACHE_TTL,
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

        jwt_manager = JWTManager(
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            access_token_expire_minutes=(
                settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        )

        refresh_token_manager = (
            RefreshTokenManager()
        )

        # Create an instance of the RegistrationService class
        self.registration_service = (
            RegistrationService(
                user_repository=user_repository,
                role_repository=role_repository,
                normalizer=normalizer,
                password_manager=password_manager,
            )
        )

        self.registration_service.audit_log_service = (
            audit_log_service
        )

        # Create an instance of the LoginService class
        self.login_service = LoginService(
            user_repository=user_repository,
            refresh_token_repository=(
                refresh_token_repository
            ),
            normalizer=normalizer,
            password_manager=password_manager,
            jwt_manager=jwt_manager,
            refresh_token_manager=(
                refresh_token_manager
            ),
            refresh_token_expire_days=(
                settings.REFRESH_TOKEN_EXPIRE_DAYS
            ),
        )

        self.login_service.audit_log_service = (
            audit_log_service
        )

        # Create an instance of the RefreshTokenService class
        self.refresh_token_service = (
            RefreshTokenService(
                user_repository=user_repository,
                refresh_token_repository=(
                    refresh_token_repository
                ),
                jwt_manager=jwt_manager,
                refresh_token_manager=(
                    refresh_token_manager
                ),
                refresh_token_expire_days=(
                    settings.REFRESH_TOKEN_EXPIRE_DAYS
                ),
            )
        )

        self.refresh_token_service.audit_log_service = (
            audit_log_service
        )

        # Create an instance of the LogoutService class
        self.logout_service = LogoutService(
            refresh_token_repository=(
                refresh_token_repository
            ),
            refresh_token_manager=(
                refresh_token_manager
            ),
        )

        self.logout_service.audit_log_service = (
            audit_log_service
        )

        # Create an instance of the TokenCleanupService class
        self.token_cleanup_service = TokenCleanupService(
            refresh_token_repository=(
                refresh_token_repository
            ),
            revoked_retention_days=(
                settings.REVOKED_TOKEN_RETENTION_DAYS
            ),
        )

        self.token_cleanup_service.audit_log_service = (
            audit_log_service
        )

    # ==============================
    # Register user
    # ==============================

    async def register(
        self,
        data: UserCreate,
    ) -> UserResponse:
        """
        Registers a new user.
        
        Args:
            data (UserCreate): The user creation data.
            
        Returns:
            UserResponse: The created user response.
        """

        return await self.registration_service.register(
            data
        )

    # ==============================
    # Login existing user
    # ==============================

    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:
        """
        Logs in an existing user.
        
        Args:
            data (LoginRequest): The login request data.
            
        Returns:
            TokenResponse: The token response for the logged-in user.
        """

        return await self.login_service.login(
            data
        )

    # ==============================
    # Rotate refresh token
    # ==============================

    async def refresh(
        self,
        data: RefreshTokenRequest,
    ) -> TokenResponse:
        """
        Rotates the refresh token for the current user.
        
        Args:
            data (RefreshTokenRequest): The refresh token request data.
            
        Returns:
            TokenResponse: The new token response with a rotated refresh token.
        """

        return await self.refresh_token_service.rotate(
            data
        )

    # ==============================
    # Logout from current session
    # ==============================

    async def logout(
        self,
        data: RefreshTokenRequest,
    ) -> None:
        """
        Logs out the current user from their current session.
        
        Args:
            data (RefreshTokenRequest): The refresh token request data.
            
        Returns:
            None
        """

        await self.logout_service.logout(
            data
        )

    # ==============================
    # Logout all sessions for given user ID
    # ==============================

    async def logout_all(
        self,
        user_id: int,
    ) -> None:
        """
        Logs out all sessions for a given user ID.
        
        Args:
            user_id (int): The ID of the user to log out.
            
        Returns:
            None
        """

        await self.logout_service.logout_all(
            user_id
        )


    # ==============================
    # Cleanup stale refresh tokens
    # ==============================

    async def cleanup_tokens(self) -> TokenCleanupResponse:
        """
        Removes expired and old revoked refresh tokens.

        Returns:
            TokenCleanupResponse: Counts of deleted rows.
        """

        return await self.token_cleanup_service.cleanup()