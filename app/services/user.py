# ==============================
# Bibliotēku imports
# ==============================

from math import ceil

from fastapi import HTTPException

from models import User

from repositories import UserRepository

from schemas.user import (
    UserAdminUpdate,
    UserListItem,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
)

from utils import (
    DataNormalizer, 
    PasswordManager
)


# ==============================
# Lietotāja atjaunošanas serviss
# ==============================

class UserUpdateService:

    def __init__(
        self,
        user_repository: UserRepository,
        normalizer: DataNormalizer,
        password_manager: PasswordManager,
    ):
        # Lietotāja repozitorijs
        self.user_repository = user_repository

        # Datu normalizators
        self.normalizer = normalizer

        # Paroļu pārvaldnieks
        self.password_manager = password_manager

    # Lietotāja atbildes shēmas izveide
    async def _build_user_response(
        self,
        user: User,
    ) -> UserResponse:

        if user.id is None:
            raise HTTPException(
                status_code=500,
                detail="User ID was not generated",
            )

        roles = await self.user_repository.get_roles(
            user.id
        )

        return UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            roles=roles,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    # Lietotāja meklēšana pēc ID
    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse:

        # Lietotāja meklēšana
        user = await self.user_repository.get_by_id(
            user_id
        )

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        # Lietotāja atbildes izveide
        return await self._build_user_response(
            user
        )

    # Lietotāja datu atjaunošana
    async def _update_user(
        self,
        user: User,
        username: str | None = None,
        full_name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        is_active: bool | None = None,
    ) -> User:

        # Lietotājvārda atjaunošana
        if username is not None:
            username = (
                self.normalizer.normalize_username(
                    username
                )
            )

            if username != user.username:
                existing_user = (
                    await self.user_repository.get_by_username(
                        username
                    )
                )

                if existing_user is not None:
                    raise HTTPException(
                        status_code=409,
                        detail="Username already exists",
                    )

                user.username = username

        # Pilnā vārda atjaunošana
        if full_name is not None:
            user.full_name = (
                self.normalizer.normalize_text(
                    full_name
                )
            )

        # E-pasta atjaunošana
        if email is not None:
            email = (
                self.normalizer.normalize_email(
                    email
                )
            )

            if email != str(user.email):
                existing_user = (
                    await self.user_repository.get_by_email(
                        email
                    )
                )

                if existing_user is not None:
                    raise HTTPException(
                        status_code=409,
                        detail="Email already exists",
                    )

                user.email = email

        # Paroles atjaunošana
        if password is not None:
            user.password_hash = (
                self.password_manager.hash_password(
                    password
                )
            )

        # Konta aktivitātes statusa atjaunošana
        if is_active is not None:
            user.is_active = is_active

        return user

    # Lietotāju meklēšana ar lapošanu
    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> UserListResponse:

        # Lappuses validācija
        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="Page must be greater than 0",
            )

        # Lapas izmēra validācija
        if page_size < 1:
            raise HTTPException(
                status_code=400,
                detail="Page size must be greater than 0",
            )

        # Maksimālais rezultātu skaits vienā lapā
        if page_size > 100:
            raise HTTPException(
                status_code=400,
                detail="Page size cannot exceed 100",
            )

        # Meklēšanas teksta normalizācija
        if query is not None:
            query = self.normalizer.normalize_text(
                query
            )

            if not query:
                query = None

        # Meklēšana
        users, total = (
            await self.user_repository.search(
                query=query,
                page=page,
                page_size=page_size,
            )
        )

        # Lietotāju saraksta izveide
        items = [
            UserListItem(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                email=user.email,
                is_active=user.is_active,
            )
            for user in users
            if user.id is not None
        ]

        # Kopējais lapu skaits
        pages = ceil(
            total / page_size
        )

        return UserListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            pages=pages,
        )

    # Lietotāja atjaunošana administratora režīmā
    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:

        try:
            # Pārbauda, vai administrators nemēģina atjaunot pats sevi
            if admin_id == user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Administrator cannot update themselves",
                )

            # Lietotāja meklēšana
            user = await self.user_repository.get_by_id(
                user_id
            )

            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User not found",
                )

            # Lietotāja datu atjaunošana
            user = await self._update_user(
                user=user,
                username=data.username,
                full_name=data.full_name,
                email=(
                    str(data.email)
                    if data.email is not None
                    else None
                ),
                password=data.password,
                is_active=data.is_active,
            )

            # Lietotāja saglabāšana
            user = await self.user_repository.update(
                user
            )

            # Izmaiņu saglabāšana
            await self.user_repository.commit()

            # Lietotāja atbildes izveide
            return await self._build_user_response(
                user
            )

        except HTTPException:
            raise

        except Exception:
            await self.user_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to update user",
            )

    # Paša lietotāja datu atjaunošana
    async def update_self(
        self,
        user_id: int,
        data: UserSelfUpdate,
    ) -> UserResponse:

        try:
            # Lietotāja meklēšana
            user = await self.user_repository.get_by_id(
                user_id
            )

            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User not found",
                )

            # Ja tiek mainīta parole,
            # jāpārbauda pašreizējā parole
            if data.password is not None:

                # Pašreizējā parole nav norādīta
                if data.current_password is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Current password is required",
                    )

                # Pašreizējā parole nav pareiza
                if not self.password_manager.verify_password(
                    data.current_password,
                    user.password_hash,
                ):
                    raise HTTPException(
                        status_code=401,
                        detail="Current password is incorrect",
                    )

            # Lietotāja datu atjaunošana
            user = await self._update_user(
                user=user,
                username=data.username,
                full_name=data.full_name,
                email=(
                    str(data.email)
                    if data.email is not None
                    else None
                ),
                password=data.password,
            )

            # Lietotāja saglabāšana
            user = await self.user_repository.update(
            user
            )

            # Izmaiņu saglabāšana
            await self.user_repository.commit()

            # Lietotāja atbildes izveide
            return await self._build_user_response(
                user
            )

        except HTTPException:
            raise

        except Exception:
            await self.user_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to update user",
            )