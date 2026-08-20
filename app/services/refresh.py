# ==============================
# Bibliotēku imports
# ==============================

from datetime import datetime, timedelta

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

        # Audit žurnāla serviss
        self.audit_log_service: AuditLogService | None = None

    # ==============================
    # Refresh tokena rotācija
    # ==============================

    async def rotate(
        self,
        data: RefreshTokenRequest,
    ) -> TokenResponse:

        try:
            # ==============================
            # Refresh tokena hešošana
            # ==============================

            token_hash = (
                self.refresh_token_manager.hash_token(
                    data.refresh_token
                )
            )

            # ==============================
            # Tokena meklēšana un rindas
            # bloķēšana
            # ==============================

            stored_token = (
                await self.refresh_token_repository
                .get_by_hash_for_update(
                    token_hash
                )
            )

            # ==============================
            # Tokens nav atrasts
            # ==============================

            if stored_token is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token",
                )

            # ==============================
            # Pārbauda tokena atsaukšanu
            # ==============================

            if stored_token.revoked:

                # Iespējama tokena atkārtota izmantošana
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

                # Audit ieraksts
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
            # Pārbauda tokena derīguma termiņu
            # ==============================

            if stored_token.expires_at <= datetime.now():

                # Tokena atsaukšana
                await (
                    self.refresh_token_repository
                    .revoke(
                        stored_token
                    )
                )

                # Izmaiņu saglabāšana
                await (
                    self.refresh_token_repository
                    .commit()
                )

                # Audit ieraksts
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
            # Lietotāja meklēšana
            # ==============================

            user = await self.user_repository.get_by_id(
                stored_token.user_id
            )

            # ==============================
            # Lietotājs nav atrasts
            # ==============================

            if user is None:

                # Audit ieraksts
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
            # Pārbauda lietotāja aktivitāti
            # ==============================

            if not user.is_active:

                # Audit ieraksts
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
            # Pārbauda lietotāja ID
            # ==============================

            if user.id is None:
                raise HTTPException(
                    status_code=500,
                    detail="User ID was not generated",
                )

            # ==============================
            # Lietotāja lomu iegūšana
            # ==============================

            roles = await self.user_repository.get_roles(
                user.id
            )

            # ==============================
            # Jauna access tokena izveide
            # ==============================

            access_token = (
                self.jwt_manager.create_access_token(
                    user_id=user.id,
                    roles=roles,
                )
            )

            # ==============================
            # Jauna refresh tokena ģenerēšana
            # ==============================

            new_refresh_token = (
                self.refresh_token_manager.generate_token()
            )

            # ==============================
            # Jaunā refresh tokena hešošana
            # ==============================

            new_token_hash = (
                self.refresh_token_manager.hash_token(
                    new_refresh_token
                )
            )

            # ==============================
            # Jaunā tokena derīguma termiņš
            # ==============================

            new_expires_at = (
                datetime.now()
                + timedelta(
                    days=self.refresh_token_expire_days
                )
            )

            # ==============================
            # Vecā tokena atsaukšana
            # ==============================

            await self.refresh_token_repository.revoke(
                stored_token
            )

            # ==============================
            # Jaunā refresh tokena modeļa izveide
            # ==============================

            new_refresh_token_model = RefreshToken(
                user_id=user.id,
                token_hash=new_token_hash,
                expires_at=new_expires_at,
            )

            # ==============================
            # Jaunā refresh tokena saglabāšana
            # ==============================

            await self.refresh_token_repository.create(
                new_refresh_token_model
            )

            # ==============================
            # Izmaiņu saglabāšana
            # ==============================

            await self.refresh_token_repository.commit()

            # ==============================
            # Veiksmīgas rotācijas ieraksts
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
            # Tokenu atgriešana
            # ==============================

            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
            )

        except HTTPException:
            # HTTP kļūdu pārsūtīšana tālāk
            raise

        except Exception:

            # Izmaiņu atcelšana
            await (
                self.refresh_token_repository
                .rollback()
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to rotate refresh token",
            )