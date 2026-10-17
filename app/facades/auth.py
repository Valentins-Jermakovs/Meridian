
# ==============================
# Third-party imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

# ==============================
# Application configuration
# ==============================

from config.config import settings

# ==============================
# Application repositories
# ==============================

from repositories import (
    AuditLogRepository,
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)

# ==============================
# Application schemas
# ==============================

from schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenCleanupResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
)

# ==============================
# Application services
# ==============================

from services import (
    AuditLogService,
    LoginService,
    LogoutService,
    RefreshTokenService,
    RegistrationService,
    TokenCleanupService,
)

# ==============================
# Application utilities
# ==============================

from utils import (
    DataNormalizer,
    JWTManager,
    PasswordManager,
    RefreshTokenManager,
)


# ==============================
# Authentication facade
# ==============================

class AuthFacade:
    """Coordinate authentication services and their dependencies."""

    def __init__(
        self,
        session: AsyncSession,
        jwt_manager: JWTManager,
    ) -> None:
        """Initialize authentication services."""

        # ==============================
        # Repositories
        # ==============================

        user_repository = UserRepository(session)
        role_repository = RoleRepository(session)
        refresh_token_repository = RefreshTokenRepository(session)
        audit_log_repository = AuditLogRepository(session)

        # ==============================
        # Audit log service
        # ==============================

        # The service retrieves the shared Redis cache internally.
        audit_log_service = AuditLogService(
            audit_log_repository=audit_log_repository,
        )

        # ==============================
        # Shared utilities
        # ==============================

        normalizer = DataNormalizer()
        password_manager = PasswordManager()
        refresh_token_manager = RefreshTokenManager()

        # ==============================
        # Registration service
        # ==============================

        self.registration_service = RegistrationService(
            user_repository=user_repository,
            role_repository=role_repository,
            normalizer=normalizer,
            password_manager=password_manager,
        )
        self.registration_service.audit_log_service = audit_log_service

        # ==============================
        # Login service
        # ==============================

        self.login_service = LoginService(
            user_repository=user_repository,
            refresh_token_repository=refresh_token_repository,
            normalizer=normalizer,
            password_manager=password_manager,
            jwt_manager=jwt_manager,
            refresh_token_manager=refresh_token_manager,
            refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )
        self.login_service.audit_log_service = audit_log_service

        # ==============================
        # Refresh token service
        # ==============================

        self.refresh_token_service = RefreshTokenService(
            user_repository=user_repository,
            refresh_token_repository=refresh_token_repository,
            jwt_manager=jwt_manager,
            refresh_token_manager=refresh_token_manager,
            refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )
        self.refresh_token_service.audit_log_service = audit_log_service

        # ==============================
        # Logout service
        # ==============================

        self.logout_service = LogoutService(
            refresh_token_repository=refresh_token_repository,
            refresh_token_manager=refresh_token_manager,
        )
        self.logout_service.audit_log_service = audit_log_service

        # ==============================
        # Token cleanup service
        # ==============================

        self.token_cleanup_service = TokenCleanupService(
            refresh_token_repository=refresh_token_repository,
            revoked_retention_days=settings.REVOKED_TOKEN_RETENTION_DAYS,
        )
        self.token_cleanup_service.audit_log_service = audit_log_service

    # ==============================
    # User registration
    # ==============================

    async def register(
        self,
        data: UserCreate,
    ) -> UserResponse:
        """Register a new user."""
        return await self.registration_service.register(data)

    # ==============================
    # User login
    # ==============================

    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:
        """Authenticate a user and issue tokens."""
        return await self.login_service.login(data)

    # ==============================
    # Refresh token rotation
    # ==============================

    async def refresh(
        self,
        data: RefreshTokenRequest,
    ) -> TokenResponse:
        """Rotate a refresh token."""
        return await self.refresh_token_service.rotate(data)

    # ==============================
    # Logout current session
    # ==============================

    async def logout(
        self,
        data: RefreshTokenRequest,
    ) -> None:
        """Log out the current refresh-token session."""
        await self.logout_service.logout(data)

    # ==============================
    # Logout all user sessions
    # ==============================

    async def logout_all(
        self,
        user_id: int,
    ) -> None:
        """Log out all sessions belonging to a user."""
        await self.logout_service.logout_all(user_id)

    # ==============================
    # Refresh token cleanup
    # ==============================

    async def cleanup_tokens(self) -> TokenCleanupResponse:
        """Remove expired and old revoked refresh tokens."""
        return await self.token_cleanup_service.cleanup()
