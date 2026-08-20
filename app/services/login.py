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
# Lietotāja autentifikācijas serviss
# ==============================

class LoginService:

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
        # Lietotāja repozitorijs
        self.user_repository = user_repository

        # Refresh tokena repozitorijs
        self.refresh_token_repository = (
            refresh_token_repository
        )

        # Datu normalizators
        self.normalizer = normalizer

        # Paroļu pārvaldnieks
        self.password_manager = password_manager

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

    # Lietotāja pieslēgšanās
    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:

        # Ievaddatu normalizācija
        login = self.normalizer.normalize_text(
            data.login
        )

        # Meklē pēc lietotājvārda
        username = self.normalizer.normalize_username(
            login
        )

        user = await self.user_repository.get_by_username(
            username
        )

        # Ja pēc username neatrada,
        # meklē pēc e-pasta
        if user is None:
            email = self.normalizer.normalize_email(
                login
            )

            user = await self.user_repository.get_by_email(
                email
            )

        # Lietotājs nav atrasts
        if user is None:

            # Neveiksmīga pieslēgšanās
            if self.audit_log_service is not None:
                await self.audit_log_service.create(
                    user_id=None,
                    action=AuditAction.FAILED_LOGIN,
                    description=(
                        f"Failed login attempt for '{login}'"
                    ),
                    success=False,
                )

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        # Pārbauda lietotāja aktivitāti
        if not user.is_active:

            # Neveiksmīga pieslēgšanās
            if self.audit_log_service is not None:
                await self.audit_log_service.create(
                    user_id=user.id,
                    action=AuditAction.FAILED_LOGIN,
                    description=(
                        f"Login attempt for inactive user "
                        f"'{user.username}'"
                    ),
                    success=False,
                )

            raise HTTPException(
                status_code=403,
                detail="User account is inactive",
            )

        # Pārbauda paroli
        if not self.password_manager.verify_password(
            data.password,
            user.password_hash,
        ):

            # Neveiksmīga pieslēgšanās
            if self.audit_log_service is not None:
                await self.audit_log_service.create(
                    user_id=user.id,
                    action=AuditAction.FAILED_LOGIN,
                    description=(
                        f"Invalid password for user "
                        f"'{user.username}'"
                    ),
                    success=False,
                )

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        if user.id is None:
            raise HTTPException(
                status_code=500,
                detail="User ID was not generated",
            )

        # Lietotāja lomu iegūšana
        roles = await self.user_repository.get_roles(
            user.id
        )

        # Access tokena izveide
        access_token = (
            self.jwt_manager.create_access_token(
                user_id=user.id,
                roles=roles,
            )
        )

        # Refresh tokena ģenerēšana
        raw_refresh_token = (
            self.refresh_token_manager.generate_token()
        )

        # Refresh tokena hešošana
        token_hash = (
            self.refresh_token_manager.hash_token(
                raw_refresh_token
            )
        )

        # Refresh tokena termiņš
        expires_at = (
            datetime.now()
            + timedelta(
                days=self.refresh_token_expire_days
            )
        )

        # Refresh tokena modeļa izveide
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        try:
            # Refresh tokena saglabāšana
            await self.refresh_token_repository.create(
                refresh_token
            )

            # Izmaiņu saglabāšana
            await self.refresh_token_repository.commit()

        except Exception:
            # Izmaiņu atcelšana
            await self.refresh_token_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to create refresh token",
            )

        # Veiksmīgas pieslēgšanās ieraksts
        if self.audit_log_service is not None:
            await self.audit_log_service.create(
                user_id=user.id,
                action=AuditAction.LOGIN,
                description=(
                    f"User '{user.username}' successfully logged in"
                ),
                success=True,
            )

        # Tokenu atgriešana
        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
        )