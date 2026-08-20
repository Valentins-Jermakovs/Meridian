# ==============================
# Bibliotēku imports
# ==============================

from fastapi import HTTPException

from repositories import RefreshTokenRepository

from schemas import RefreshTokenRequest

from utils import RefreshTokenManager


# ==============================
# Lietotāja atteikšanās serviss
# ==============================

class LogoutService:

    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
        refresh_token_manager: RefreshTokenManager,
    ):
        # Refresh tokena repozitorijs
        self.refresh_token_repository = (
            refresh_token_repository
        )

        # Refresh tokena pārvaldnieks
        self.refresh_token_manager = (
            refresh_token_manager
        )

    # Atteikšanās no pašreizējās sesijas
    async def logout(
        self,
        data: RefreshTokenRequest,
    ) -> None:

        try:
            # Refresh tokena hešošana
            token_hash = (
                self.refresh_token_manager.hash_token(
                    data.refresh_token
                )
            )

            # Refresh tokena meklēšana
            refresh_token = (
                await self.refresh_token_repository.get_by_hash(
                    token_hash
                )
            )

            # Tokens nav atrasts
            if refresh_token is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token",
                )

            # Tokens jau ir atsaukts
            if refresh_token.revoked:
                raise HTTPException(
                    status_code=401,
                    detail="Refresh token already revoked",
                )

            # Tokena atsaukšana
            await self.refresh_token_repository.revoke(
                refresh_token
            )

            # Izmaiņu saglabāšana
            await self.refresh_token_repository.commit()

        except HTTPException:
            raise

        except Exception:
            await self.refresh_token_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to logout",
            )

    # Atteikšanās no visām sesijām
    async def logout_all(
        self,
        user_id: int,
    ) -> None:

        try:
            # Visu lietotāja refresh tokenu atsaukšana
            await self.refresh_token_repository.revoke_all_by_user(
                user_id
            )

            # Izmaiņu saglabāšana
            await self.refresh_token_repository.commit()

        except Exception:
            await self.refresh_token_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to logout from all sessions",
            )