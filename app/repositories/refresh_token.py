# ==============================
# Bibliotēku imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import (
    select,
    update,
)

from models import RefreshToken


# ==============================
# Refresh tokena repozitorijs
# ==============================

class RefreshTokenRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        # Datu bāzes sesija
        self.session = session

    # ==============================
    # Refresh tokena meklēšana pēc heša
    # ==============================

    async def get_by_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:

        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )

        return result.scalar_one_or_none()

    # ==============================
    # Refresh tokena meklēšana
    # ar rindas bloķēšanu
    # ==============================

    async def get_by_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshToken | None:

        result = await self.session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()

    # ==============================
    # Refresh tokena izveide
    # ==============================

    async def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:

        self.session.add(
            refresh_token
        )

        await self.session.flush()

        return refresh_token

    # ==============================
    # Refresh tokena atsaukšana
    # ==============================

    async def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:

        refresh_token.revoked = True

        self.session.add(
            refresh_token
        )

        await self.session.flush()

        return refresh_token

    # ==============================
    # Visu lietotāja refresh tokenu
    # atsaukšana
    # ==============================

    async def revoke_all_by_user(
        self,
        user_id: int,
    ) -> None:

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

    # ==============================
    # Izmaiņu saglabāšana
    # ==============================

    async def commit(self):
        await self.session.commit()

    # ==============================
    # Izmaiņu atcelšana
    # ==============================

    async def rollback(self):
        await self.session.rollback()