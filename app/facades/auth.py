# ==============================
# Bibliotēku imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import (
    UserRepository,
    RoleRepository,
    RefreshTokenRepository,
)

from schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

from services.login import LoginService
from services.logout import LogoutService
from services.refresh import RefreshTokenService
from services.registration import RegistrationService

from utils import (
    DataNormalizer,
    PasswordManager,
    JWTManager,
    RefreshTokenManager,
)

from config.config import settings


# ==============================
# Autentifikācijas fasāde
# ==============================

class AuthFacade:

    def __init__(
        self,
        session: AsyncSession,
    ):
        # Repozitoriji
        user_repository = UserRepository(
            session
        )

        role_repository = RoleRepository(
            session
        )

        refresh_token_repository = (
            RefreshTokenRepository(
                session
            )
        )

        # Utilītas
        normalizer = DataNormalizer()

        password_manager = PasswordManager()

        jwt_manager = JWTManager(
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            access_token_expire_minutes=(
                settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        )

        refresh_token_manager = (
            RefreshTokenManager()
        )

        # Reģistrācijas serviss
        self.registration_service = (
            RegistrationService(
                user_repository=user_repository,
                role_repository=role_repository,
                normalizer=normalizer,
                password_manager=password_manager,
            )
        )

        # Pieslēgšanās serviss
        self.login_service = LoginService(
            user_repository=user_repository,
            refresh_token_repository=(
                refresh_token_repository
            ),
            normalizer=normalizer,
            password_manager=password_manager,
            jwt_manager=jwt_manager,
            refresh_token_manager=(
                refresh_token_manager
            ),
            refresh_token_expire_days=(
                settings.REFRESH_TOKEN_EXPIRE_DAYS
            ),
        )

        # Refresh tokena serviss
        self.refresh_token_service = (
            RefreshTokenService(
                user_repository=user_repository,
                refresh_token_repository=(
                    refresh_token_repository
                ),
                jwt_manager=jwt_manager,
                refresh_token_manager=(
                    refresh_token_manager
                ),
                refresh_token_expire_days=(
                    settings.REFRESH_TOKEN_EXPIRE_DAYS
                ),
            )
        )

        # Atteikšanās serviss
        self.logout_service = LogoutService(
            refresh_token_repository=(
                refresh_token_repository
            ),
            refresh_token_manager=(
                refresh_token_manager
            ),
        )

    # Lietotāja reģistrācija
    async def register(
        self,
        data: UserCreate,
    ) -> UserResponse:

        return await self.registration_service.register(
            data
        )

    # Lietotāja pieslēgšanās
    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:

        return await self.login_service.login(
            data
        )

    # Refresh tokena rotācija
    async def refresh(
        self,
        data: RefreshTokenRequest,
    ) -> TokenResponse:

        return await self.refresh_token_service.rotate(
            data
        )

    # Atteikšanās no pašreizējās sesijas
    async def logout(
        self,
        data: RefreshTokenRequest,
    ) -> None:

        await self.logout_service.logout(
            data
        )

    # Atteikšanās no visām sesijām
    async def logout_all(
        self,
        user_id: int,
    ) -> None:

        await self.logout_service.logout_all(
            user_id
        )