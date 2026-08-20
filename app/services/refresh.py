# ==============================
# Bibliotēku imports
# ==============================

from datetime import datetime, timedelta

from models import RefreshToken

from repositories.user import UserRepository
from repositories.refresh_token import RefreshTokenRepository

from utils.jwt import JWTManager
from utils.refresh_token import RefreshTokenManager


# ==============================
# Refresh tokena serviss
# ==============================

class RefreshTokenService:

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_manager: JWTManager,
        refresh_token_manager: RefreshTokenManager,
        refresh_token_expire_days: int,
    ):
        # Lietotāja repozitorijs
        self.user_repository = user_repository

        # Refresh tokena repozitorijs
        self.refresh_token_repository = (
            refresh_token_repository
        )

        # JWT pārvaldnieks
        self.jwt_manager = jwt_manager

        # Refresh tokena pārvaldnieks
        self.refresh_token_manager = (
            refresh_token_manager
        )

        # Refresh tokena derīguma termiņš
        self.refresh_token_expire_days = (
            refresh_token_expire_days
        )

    # Refresh tokena rotācija
    async def rotate(
        self,
        refresh_token: str,
    ) -> dict:

        try:
            # Refresh tokena hešošana
            token_hash = (
                self.refresh_token_manager.hash_token(
                    refresh_token
                )
            )

            # Tokena meklēšana un rindas bloķēšana
            stored_token = (
                await self.refresh_token_repository
                .get_by_hash_for_update(
                    token_hash
                )
            )

            if stored_token is None:
                raise ValueError(
                    "Invalid refresh token"
                )

            # Pārbauda, vai tokens jau ir atsaukts
            if stored_token.revoked:

                # Iespējamā tokena atkārtota izmantošana
                await self.refresh_token_repository.revoke_all_by_user(
                    stored_token.user_id
                )

                await self.refresh_token_repository.commit()

                raise ValueError(
                    "Refresh token reuse detected"
                )

            # Pārbauda tokena derīguma termiņu
            if stored_token.expires_at <= datetime.now():
                await self.refresh_token_repository.revoke(
                    stored_token
                )

                await self.refresh_token_repository.commit()

                raise ValueError(
                    "Refresh token expired"
                )

            # Lietotāja meklēšana
            user = await self.user_repository.get_by_id(
                stored_token.user_id
            )

            if user is None:
                raise ValueError(
                    "User not found"
                )

            # Pārbauda lietotāja aktivitāti
            if not user.is_active:
                raise ValueError(
                    "User account is inactive"
                )

            if user.id is None:
                raise ValueError(
                    "User ID was not generated"
                )

            # Lietotāja lomu iegūšana
            roles = await self.user_repository.get_roles(
                user.id
            )

            # Jauna access tokena izveide
            access_token = (
                self.jwt_manager.create_access_token(
                    user_id=user.id,
                    roles=roles,
                )
            )

            # Jauna refresh tokena izveide
            new_refresh_token = (
                self.refresh_token_manager.generate_token()
            )

            new_token_hash = (
                self.refresh_token_manager.hash_token(
                    new_refresh_token
                )
            )

            new_expires_at = datetime.now() + timedelta(
                days=self.refresh_token_expire_days
            )

            # Vecā tokena atsaukšana
            await self.refresh_token_repository.revoke(
                stored_token
            )

            # Jaunā tokena saglabāšana
            new_refresh_token_model = RefreshToken(
                user_id=user.id,
                token_hash=new_token_hash,
                expires_at=new_expires_at,
            )

            await self.refresh_token_repository.create(
                new_refresh_token_model
            )

            # Izmaiņu saglabāšana
            await self.refresh_token_repository.commit()

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            }

        except Exception:
            await self.refresh_token_repository.rollback()

            raise