# ==============================
# Repository Imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import (
    select,
    update,
    delete
)

from datetime import (
    datetime, 
    timedelta
)

from models import RefreshToken


# ==============================
# Refresh Token Repository
# ==============================

class RefreshTokenRepository:
    """
    A repository for refresh token data storage and retrieval.
    
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
        self.session = session


    # Get a refresh token by its hash
    async def get_by_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        """
        Gets a refresh token by its hash.
        
        Args:
            token_hash (str): The hash of the refresh token.
        
        Returns:
            RefreshToken | None: The refresh token if found, otherwise None.
        """
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )

        return result.scalar_one_or_none()


    # Get a refresh token by its hash for update
    async def get_by_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        """
        Gets a refresh token by its hash with row-level locking.
        
        Args:
            token_hash (str): The hash of the refresh token.
        
        Returns:
            RefreshToken | None: The refresh token if found, otherwise None.
        """
        result = await self.session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()


    # Create a new refresh token
    async def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        """
        Creates a new refresh token and adds it to the database.
        
        Args:
            refresh_token (RefreshToken): The refresh token to be created.
        
        Returns:
            RefreshToken: The newly created refresh token.
        """
        self.session.add(
            refresh_token
        )

        await self.session.flush()

        return refresh_token


    # Revoke a refresh token
    async def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        """
        Revokes a refresh token by setting its revoked flag to True.
        
        Args:
            refresh_token (RefreshToken): The refresh token to be revoked.
        
        Returns:
            RefreshToken: The revoked refresh token.
        """
        refresh_token.revoked = True

        self.session.add(
            refresh_token
        )

        await self.session.flush()

        return refresh_token


    # Revoke all refresh tokens for a user
    async def revoke_all_by_user(
        self,
        user_id: int,
    ) -> None:
        """
        Revokes all refresh tokens for a given user.
        
        Args:
            user_id (int): The ID of the user.
        """
        await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(
                revoked=True,
            )
        )

        await self.session.flush()


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


    # ==============================
    # Delete Expired, Non-Revoked Refresh Tokens
    # ==============================

    async def delete_expired(self) -> int:
        """
        Deletes refresh tokens that have expired and were NOT
        revoked (i.e. tokens that simply went stale without being
        rotated, logged out, or flagged for reuse).

        Revoked tokens are intentionally excluded here — they are
        retained for the configured retention period and removed
        separately via delete_revoked_older_than, so that audit /
        reuse-detection has a window to inspect them even after
        their natural expiry.

        Returns:
            int: The number of deleted rows.
        """

        result = await self.session.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at <= datetime.now(),
                RefreshToken.revoked.is_(False),
            )
        )

        await self.session.flush()

        return result.rowcount or 0


    # ==============================
    # Delete Old Revoked Refresh Tokens
    # ==============================

    async def delete_revoked_older_than(
        self,
        days: int,
    ) -> int:
        """
        Deletes revoked refresh tokens created earlier than the given
        number of days. Non-revoked tokens are untouched here,
        regardless of expiry — that's delete_expired's job.

        Args:
            days (int): Age threshold in days for revoked tokens.

        Returns:
            int: The number of deleted rows.
        """

        cutoff = datetime.now() - timedelta(days=days)

        result = await self.session.execute(
            delete(RefreshToken).where(
                RefreshToken.revoked.is_(True),
                RefreshToken.created_at <= cutoff,
            )
        )

        await self.session.flush()

        return result.rowcount or 0


    # ==============================
    # Count Active Tokens (optional, for stats/testing)
    # ==============================

    async def count_active(self) -> int:
        """
        Counts non-revoked, non-expired refresh tokens.

        Returns:
            int: The number of active refresh tokens.
        """

        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > datetime.now(),
            )
        )

        return len(result.scalars().all())