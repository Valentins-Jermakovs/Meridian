# ==============================
# Library Imports
# ==============================

from datetime import (
    datetime, 
    timedelta
)

from fastapi import HTTPException

from models import (
    AuditAction,
    RefreshToken,
)

from repositories import (
    RefreshTokenRepository,
    UserRepository,
)

from schemas import (
    LoginRequest,
    TokenResponse,
)

from services import AuditLogService

from utils import (
    DataNormalizer,
    JWTManager,
    PasswordManager,
    RefreshTokenManager,
)


# ==============================
# User Authentication Service
# ==============================

class LoginService:
    """
    Provides authentication logic for user login.

    The service validates user credentials, checks account status,
    generates access and refresh tokens, stores the refresh token,
    and records successful or failed login attempts in the audit log.
    """


    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        normalizer: DataNormalizer,
        password_manager: PasswordManager,
        jwt_manager: JWTManager,
        refresh_token_manager: RefreshTokenManager,
        refresh_token_expire_days: int,
    ):
        """
        Initializes the user authentication service.

        Args:
            user_repository (UserRepository):
                Repository used to access user data.
            refresh_token_repository (RefreshTokenRepository):
                Repository used to manage refresh tokens.
            normalizer (DataNormalizer):
                Utility used to normalize user input.
            password_manager (PasswordManager):
                Utility used to verify user passwords.
            jwt_manager (JWTManager):
                Utility used to create access tokens.
            refresh_token_manager (RefreshTokenManager):
                Utility used to generate and hash refresh tokens.
            refresh_token_expire_days (int):
                Number of days before a refresh token expires.
        """

        # User repository
        self.user_repository = user_repository

        # Refresh token repository
        self.refresh_token_repository = (
            refresh_token_repository
        )

        # Data normalizer
        self.normalizer = normalizer

        # Password manager
        self.password_manager = password_manager

        # JWT manager
        self.jwt_manager = jwt_manager

        # Refresh token manager
        self.refresh_token_manager = (
            refresh_token_manager
        )

        # Refresh token expiration period
        self.refresh_token_expire_days = (
            refresh_token_expire_days
        )

        # Audit log service
        self.audit_log_service: AuditLogService | None = None


    # ==============================
    # User Login
    # ==============================

    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:
        """
        Authenticates a user and generates authentication tokens.

        The method normalizes the login identifier, validates the
        user's credentials and account status, creates an access
        token and refresh token, and records the login attempt.

        Args:
            data (LoginRequest): User login credentials.

        Returns:
            TokenResponse: Generated access and refresh tokens.

        Raises:
            HTTPException: If the credentials are invalid, the account
                is inactive, the user ID is missing, or the refresh
                token cannot be stored.
        """

        # ==============================
        # Normalize Input Data
        # ==============================

        login = self.normalizer.normalize_text(
            data.login
        )

        # ==============================
        # Find User
        # ==============================

        user = (
            await self.user_repository.get_by_login(
                login
            )
        )

        # ==============================
        # User Not Found
        # ==============================

        if user is None:

            # Record failed login attempt
            if self.audit_log_service is not None:

                await self.audit_log_service.create(
                    user_id=None,
                    action=AuditAction.FAILED_LOGIN,
                    description=(
                        f"Failed login attempt "
                        f"for '{login}'"
                    ),
                    success=False,
                )

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        # ==============================
        # Check User Account Status
        # ==============================

        if not user.is_active:

            # Record failed login attempt
            if self.audit_log_service is not None:

                await self.audit_log_service.create(
                    user_id=user.id,
                    action=AuditAction.FAILED_LOGIN,
                    description=(
                        f"Login attempt for "
                        f"inactive user "
                        f"'{user.username}'"
                    ),
                    success=False,
                )

            raise HTTPException(
                status_code=403,
                detail="User account is inactive",
            )

        # ==============================
        # Verify Password
        # ==============================

        password_valid = (
            await self.password_manager.verify_password(
                data.password,
                user.password_hash,
            )
        )

        if not password_valid:

            # Record failed login attempt
            if self.audit_log_service is not None:

                await self.audit_log_service.create(
                    user_id=user.id,
                    action=AuditAction.FAILED_LOGIN,
                    description=(
                        f"Invalid password "
                        f"for user "
                        f"'{user.username}'"
                    ),
                    success=False,
                )

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        # ==============================
        # Validate User ID
        # ==============================

        if user.id is None:
            raise HTTPException(
                status_code=500,
                detail="User ID was not generated",
            )

        # ==============================
        # Get User Roles
        # ==============================

        roles = await self.user_repository.get_roles(
            user.id
        )

        # ==============================
        # Create Access Token
        # ==============================

        access_token = (
            self.jwt_manager.create_access_token(
                user_id=user.id,
                roles=roles,
            )
        )

        # ==============================
        # Generate Refresh Token
        # ==============================

        raw_refresh_token = (
            self.refresh_token_manager.generate_token()
        )

        # ==============================
        # Hash Refresh Token
        # ==============================

        token_hash = (
            self.refresh_token_manager.hash_token(
                raw_refresh_token
            )
        )

        # ==============================
        # Calculate Token Expiration
        # ==============================

        expires_at = (
            datetime.now()
            + timedelta(
                days=self.refresh_token_expire_days
            )
        )

        # ==============================
        # Create Refresh Token Model
        # ==============================

        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        try:
            # ==============================
            # Save Refresh Token
            # ==============================

            await self.refresh_token_repository.create(
                refresh_token
            )

            # ==============================
            # Commit Changes
            # ==============================

            await self.refresh_token_repository.commit()

        except Exception:

            # Roll back the transaction
            await self.refresh_token_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to create refresh token",
            )

        # ==============================
        # Record Successful Login
        # ==============================

        if self.audit_log_service is not None:

            await self.audit_log_service.create(
                user_id=user.id,
                action=AuditAction.LOGIN,
                description=(
                    f"User '{user.username}' "
                    "successfully logged in"
                ),
                success=True,
            )

        # ==============================
        # Return Authentication Tokens
        # ==============================

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
        )