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
    RefreshTokenRequest,
    TokenResponse,
)

from services import AuditLogService

from utils import (
    JWTManager,
    RefreshTokenManager,
)


# ==============================
# Refresh Token Service
# ==============================

class RefreshTokenService:
    """
    Provides functionality for validating and rotating refresh tokens.

    The service validates the current refresh token, checks its
    expiration and revocation status, verifies the associated user,
    generates new authentication tokens, and revokes the old token.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_manager: JWTManager,
        refresh_token_manager: RefreshTokenManager,
        refresh_token_expire_days: int,
    ):
        """
        Initializes the refresh token service.

        Args:
            user_repository (UserRepository):
                Repository used to access user data.
            refresh_token_repository (RefreshTokenRepository):
                Repository used to manage refresh tokens.
            jwt_manager (JWTManager):
                Utility used to create access tokens.
            refresh_token_manager (RefreshTokenManager):
                Utility used to generate and hash refresh tokens.
            refresh_token_expire_days (int):
                Number of days before a new refresh token expires.
        """

        # User repository
        self.user_repository = user_repository

        # Refresh token repository
        self.refresh_token_repository = (
            refresh_token_repository
        )

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
    # Refresh Token Rotation
    # ==============================

    async def rotate(
        self,
        data: RefreshTokenRequest,
    ) -> TokenResponse:
        """
        Validates and rotates a refresh token.

        The current refresh token is locked during the operation to
        prevent concurrent reuse. A new access token and refresh token
        are generated, while the previous refresh token is revoked.

        If a revoked token is reused, all refresh tokens belonging to
        the user are revoked as a security measure.

        Args:
            data (RefreshTokenRequest):
                Request containing the refresh token to rotate.

        Returns:
            TokenResponse: Newly generated access and refresh tokens.

        Raises:
            HTTPException: If the refresh token is invalid, revoked,
                expired, the associated user cannot be found, the user
                account is inactive, or token rotation fails.
        """

        try:
            # ==============================
            # Hash Refresh Token
            # ==============================

            token_hash = (
                self.refresh_token_manager.hash_token(
                    data.refresh_token
                )
            )

            # ==============================
            # Find and Lock Refresh Token
            # ==============================

            stored_token = (
                await self.refresh_token_repository
                .get_by_hash_for_update(
                    token_hash
                )
            )

            # ==============================
            # Token Not Found
            # ==============================

            if stored_token is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token",
                )

            # ==============================
            # Check Token Revocation
            # ==============================

            if stored_token.revoked:

                # Revoke all user refresh tokens
                await (
                    self.refresh_token_repository
                    .revoke_all_by_user(
                        stored_token.user_id
                    )
                )

                await (
                    self.refresh_token_repository
                    .commit()
                )

                # Record token reuse attempt
                if self.audit_log_service is not None:

                    await self.audit_log_service.create(
                        user_id=stored_token.user_id,
                        action=AuditAction.TOKEN_REUSE,
                        description=(
                            "Refresh token reuse detected"
                        ),
                        success=False,
                    )

                raise HTTPException(
                    status_code=401,
                    detail="Refresh token reuse detected",
                )

            # ==============================
            # Check Token Expiration
            # ==============================

            if stored_token.expires_at <= datetime.now():

                # Revoke the expired token
                await (
                    self.refresh_token_repository
                    .revoke(
                        stored_token
                    )
                )

                # Commit the changes
                await (
                    self.refresh_token_repository
                    .commit()
                )

                # Record expired token attempt
                if self.audit_log_service is not None:

                    await self.audit_log_service.create(
                        user_id=stored_token.user_id,
                        action=AuditAction.REFRESH,
                        description=(
                            "Refresh token expired"
                        ),
                        success=False,
                    )

                raise HTTPException(
                    status_code=401,
                    detail="Refresh token expired",
                )

            # ==============================
            # Find User
            # ==============================

            user = await self.user_repository.get_by_id(
                stored_token.user_id
            )

            # ==============================
            # User Not Found
            # ==============================

            if user is None:

                # Record failed token rotation
                if self.audit_log_service is not None:

                    await self.audit_log_service.create(
                        user_id=stored_token.user_id,
                        action=AuditAction.REFRESH,
                        description=(
                            "Refresh token rotation "
                            "failed: user not found"
                        ),
                        success=False,
                    )

                raise HTTPException(
                    status_code=401,
                    detail="User not found",
                )

            # ==============================
            # Check User Account Status
            # ==============================

            if not user.is_active:

                # Record failed token rotation
                if self.audit_log_service is not None:

                    await self.audit_log_service.create(
                        user_id=user.id,
                        action=AuditAction.REFRESH,
                        description=(
                            "Refresh token rotation "
                            "failed: user account "
                            "is inactive"
                        ),
                        success=False,
                    )

                raise HTTPException(
                    status_code=403,
                    detail="User account is inactive",
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
            # Create New Access Token
            # ==============================

            access_token = (
                self.jwt_manager.create_access_token(
                    user_id=user.id,
                    roles=roles,
                )
            )

            # ==============================
            # Generate New Refresh Token
            # ==============================

            new_refresh_token = (
                self.refresh_token_manager.generate_token()
            )

            # ==============================
            # Hash New Refresh Token
            # ==============================

            new_token_hash = (
                self.refresh_token_manager.hash_token(
                    new_refresh_token
                )
            )

            # ==============================
            # Calculate New Token Expiration
            # ==============================

            new_expires_at = (
                datetime.now()
                + timedelta(
                    days=self.refresh_token_expire_days
                )
            )

            # ==============================
            # Revoke Old Refresh Token
            # ==============================

            await self.refresh_token_repository.revoke(
                stored_token
            )

            # ==============================
            # Create New Refresh Token Model
            # ==============================

            new_refresh_token_model = RefreshToken(
                user_id=user.id,
                token_hash=new_token_hash,
                expires_at=new_expires_at,
            )

            # ==============================
            # Save New Refresh Token
            # ==============================

            await self.refresh_token_repository.create(
                new_refresh_token_model
            )

            # ==============================
            # Commit Changes
            # ==============================

            await self.refresh_token_repository.commit()

            # ==============================
            # Record Successful Rotation
            # ==============================

            if self.audit_log_service is not None:

                await self.audit_log_service.create(
                    user_id=user.id,
                    action=AuditAction.REFRESH,
                    description=(
                        "Refresh token rotated "
                        "successfully"
                    ),
                    success=True,
                )

            # ==============================
            # Return New Tokens
            # ==============================

            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
            )

        except HTTPException:
            # Re-raise HTTP errors without modification
            raise

        except Exception:

            # Roll back the transaction
            await (
                self.refresh_token_repository
                .rollback()
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to rotate refresh token",
            )