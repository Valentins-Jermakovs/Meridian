# ==============================
# Library Imports
# ==============================

from fastapi import HTTPException

from models import AuditAction

from repositories import RefreshTokenRepository

from schemas import TokenCleanupResponse

from services import AuditLogService


# ==============================
# Token Cleanup Service
# ==============================

class TokenCleanupService:
    """
    Provides functionality for removing stale refresh tokens from
    the database:
      - Non-revoked tokens that have simply expired.
      - Revoked tokens older than a configurable retention period
        (kept around temporarily for audit / reuse-detection).
    """

    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
        revoked_retention_days: int = 30,
    ):
        """
        Args:
            refresh_token_repository (RefreshTokenRepository):
                Repository used to manage refresh tokens.
            revoked_retention_days (int):
                Number of days to keep revoked tokens before they
                are eligible for deletion (kept for audit purposes).
        """

        self.refresh_token_repository = refresh_token_repository
        self.revoked_retention_days = revoked_retention_days
        self.audit_log_service: AuditLogService | None = None

    # ==============================
    # Run Cleanup
    # ==============================

    async def cleanup(self) -> TokenCleanupResponse:
        """
        Deletes expired (non-revoked) refresh tokens and old revoked
        refresh tokens.

        Returns:
            TokenCleanupResponse: Counts of deleted rows.

        Raises:
            HTTPException: If the cleanup operation fails.
        """

        try:
            expired_count = (
                await self.refresh_token_repository.delete_expired()
            )

            revoked_count = (
                await self.refresh_token_repository
                .delete_revoked_older_than(
                    self.revoked_retention_days
                )
            )

            await self.refresh_token_repository.commit()

        except Exception:
            await self.refresh_token_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to clean up refresh tokens",
            )

        # Аудит — некритичный side-effect, не должен рушить уже
        # закоммиченный результат очистки токенов.
        if self.audit_log_service is not None:
            try:
                await self.audit_log_service.create(
                    user_id=None,
                    action=AuditAction.TOKEN_CLEANUP,
                    description=(
                        f"Token cleanup: {expired_count} expired, "
                        f"{revoked_count} old revoked tokens removed"
                    ),
                    success=True,
                )
            except HTTPException:
                pass

        return TokenCleanupResponse(
            expired_deleted=expired_count,
            revoked_deleted=revoked_count,
        )