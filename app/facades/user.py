# ==============================
# Bibliotēku imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import (
    UserRepository,
    RoleRepository,
    AuditLogRepository,
)

from schemas import (
    UserAdminUpdate,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
)

from services import AuditLogService

from services.user import UserUpdateService

from utils import (
    DataNormalizer,
    PasswordManager,
    RedisCache,
)


# ==============================
# Lietotāja fasāde
# ==============================

class UserFacade:

    def __init__(
        self,
        session: AsyncSession,
        redis_cache: RedisCache,
    ):
        # ==============================
        # Repozitoriji
        # ==============================

        user_repository = UserRepository(
            session
        )

        role_repository = RoleRepository(
            session
        )

        audit_log_repository = (
            AuditLogRepository(
                session
            )
        )

        # ==============================
        # Audit žurnāla serviss
        # ==============================

        audit_log_service = AuditLogService(
            audit_log_repository=(
                audit_log_repository
            ),
            redis_cache=redis_cache,
        )

        # ==============================
        # Utilītas
        # ==============================

        normalizer = DataNormalizer()

        password_manager = PasswordManager()

        # ==============================
        # Lietotāja serviss
        # ==============================

        self.user_service = UserUpdateService(
            user_repository=user_repository,
            role_repository=role_repository,
            normalizer=normalizer,
            password_manager=password_manager,
            redis_cache=redis_cache,
        )

        # ==============================
        # Audit servisa piesaiste
        # ==============================

        self.user_service.audit_log_service = (
            audit_log_service
        )

    # ==============================
    # Lietotāja iegūšana pēc ID
    # ==============================

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse:

        return await self.user_service.get_by_id(
            user_id
        )

    # ==============================
    # Lietotāju meklēšana
    # ==============================

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

    # ==============================
    # Administratora lietotāja
    # atjaunošana
    # ==============================

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

    # ==============================
    # Paša lietotāja datu atjaunošana
    # ==============================

    async def update_self(
        self,
        user_id: int,
        data: UserSelfUpdate,
    ) -> UserResponse:

        return await self.user_service.update_self(
            user_id=user_id,
            data=data,
        )