# ==============================
# Bibliotēku imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import UserRepository

from schemas import (
    UserAdminUpdate,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
)

from services.user import UserUpdateService

from utils import (
    DataNormalizer,
    PasswordManager,
)


# ==============================
# Lietotāja fasāde
# ==============================

class UserFacade:

    def __init__(
        self,
        session: AsyncSession,
    ):
        # Lietotāja repozitorijs
        user_repository = UserRepository(
            session
        )

        # Utilītas
        normalizer = DataNormalizer()

        password_manager = PasswordManager()

        # Lietotāja serviss
        self.user_service = UserUpdateService(
            user_repository=user_repository,
            normalizer=normalizer,
            password_manager=password_manager,
        )

    # Lietotāju meklēšana
    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> UserListResponse:

        return await self.user_service.search(
            query=query,
            page=page,
            page_size=page_size,
        )

    # Administratora lietotāja atjaunošana
    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:

        return await self.user_service.update_by_admin(
            admin_id=admin_id,
            user_id=user_id,
            data=data,
        )

    # Paša lietotāja atjaunošana
    async def update_self(
        self,
        user_id: int,
        data: UserSelfUpdate,
    ) -> UserResponse:

        return await self.user_service.update_self(
            user_id=user_id,
            data=data,
        )