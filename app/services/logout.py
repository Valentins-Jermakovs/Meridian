# ==============================
# Library Imports
# ==============================

from fastapi import HTTPException

from models import AuditAction

from repositories import RefreshTokenRepository

from schemas import RefreshTokenRequest

from services import AuditLogService

from utils import RefreshTokenManager


# ==============================
# User Logout Service
# ==============================

class LogoutService:
    """
    Provides functionality for logging users out and revoking
    their refresh tokens.
    """


    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
        refresh_token_manager: RefreshTokenManager,
    ):
        """
        Initializes the user logout service.

        Args:
            refresh_token_repository (RefreshTokenRepository):
                Repository used to access and manage refresh tokens.
            refresh_token_manager (RefreshTokenManager):
                Utility used to hash refresh tokens.
        """

        # Refresh token repository
        self.refresh_token_repository = (
            refresh_token_repository
        )

        # Refresh token manager
        self.refresh_token_manager = (
            refresh_token_manager
        )

        # Audit log service
        self.audit_log_service: AuditLogService | None = None


    # ==============================
    # Logout Current Session
    # ==============================

    async def logout(
        self,
        data: RefreshTokenRequest,
    ) -> None:
        """
        Logs the user out from the current session.

        The refresh token is hashed and searched in the database.
        If the token is valid and has not been revoked, it is revoked
        and the change is committed.

        Args:
            data (RefreshTokenRequest):
                Request containing the refresh token.

        Raises:
            HTTPException: If the refresh token is invalid, already
                revoked, or an unexpected error occurs.
        """

        try:
            # Hash the refresh token
            token_hash = (
                self.refresh_token_manager.hash_token(
                    data.refresh_token
                )
            )

            # Find the refresh token
            refresh_token = (
                await self.refresh_token_repository.get_by_hash(
                    token_hash
                )
            )

            # Token was not found
            if refresh_token is None:

                # Record failed logout attempt
                if self.audit_log_service is not None:
                    await self.audit_log_service.create(
                        user_id=None,
                        action=AuditAction.LOGOUT,
                        description=(
                            "Logout failed: invalid refresh token"
                        ),
                        success=False,
                    )

                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token",
                )

            # Token has already been revoked
            if refresh_token.revoked:

                # Record failed logout attempt
                if self.audit_log_service is not None:
                    await self.audit_log_service.create(
                        user_id=refresh_token.user_id,
                        action=AuditAction.LOGOUT,
                        description=(
                            "Logout failed: "
                            "refresh token already revoked"
                        ),
                        success=False,
                    )

                raise HTTPException(
                    status_code=401,
                    detail="Refresh token already revoked",
                )

            # Revoke the refresh token
            await self.refresh_token_repository.revoke(
                refresh_token
            )

            # Commit the changes
            await self.refresh_token_repository.commit()

            # Record successful logout
            if self.audit_log_service is not None:
                await self.audit_log_service.create(
                    user_id=refresh_token.user_id,
                    action=AuditAction.LOGOUT,
                    description=(
                        "User successfully logged out"
                    ),
                    success=True,
                )

        except HTTPException:
            raise

        except Exception:
            # Roll back the transaction
            await self.refresh_token_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to logout",
            )


    # ==============================
    # Logout From All Sessions
    # ==============================

    async def logout_all(
        self,
        user_id: int,
    ) -> None:
        """
        Logs the user out from all active sessions.

        All refresh tokens associated with the specified user are
        revoked and the changes are committed to the database.

        Args:
            user_id (int): Unique identifier of the user.

        Raises:
            HTTPException: If the refresh tokens cannot be revoked.
        """

        try:
            # Revoke all refresh tokens belonging to the user
            await self.refresh_token_repository.revoke_all_by_user(
                user_id
            )

            # Commit the changes
            await self.refresh_token_repository.commit()

            # Record successful logout from all sessions
            if self.audit_log_service is not None:
                await self.audit_log_service.create(
                    user_id=user_id,
                    action=AuditAction.LOGOUT_ALL,
                    description=(
                        "User successfully logged out "
                        "from all sessions"
                    ),
                    success=True,
                )

        except Exception:
            # Roll back the transaction
            await self.refresh_token_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to logout from all sessions",
            )