# ==============================
# Bibliotēku imports
# ==============================

from math import ceil

from fastapi import HTTPException

from models import User

from repositories import (
    UserRepository,
    RoleRepository,
)

from schemas.user import (
    UserAdminUpdate,
    UserListItem,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
)

from utils import (
    DataNormalizer,
    PasswordManager,
    RedisCache,
)


# ==============================
# Lietotāja atjaunošanas serviss
# ==============================

class UserUpdateService:

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        normalizer: DataNormalizer,
        password_manager: PasswordManager,
        redis_cache: RedisCache,
    ):
        # Lietotāja repozitorijs
        self.user_repository = user_repository

        # Lomas repozitorijs
        self.role_repository = role_repository

        # Datu normalizators
        self.normalizer = normalizer

        # Paroļu pārvaldnieks
        self.password_manager = password_manager

        # Redis kešatmiņa
        self.redis_cache = redis_cache

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

        # Redis atslēga
        cache_key = f"user:{user_id}"

        # Meklē Redis kešatmiņā
        cached_user = await self.redis_cache.get(
            cache_key
        )

        if cached_user is not None:
            return UserResponse.model_validate(
                cached_user
            )

        # Meklē PostgreSQL
        user = await self.user_repository.get_by_id(
            user_id
        )

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        # Izveido atbildi
        response = await self._build_user_response(
            user
        )

        # Saglabā Redis
        await self.redis_cache.set(
            cache_key,
            response.model_dump(
                mode="json"
            ),
        )

        return response

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

        # Redis atslēga
        cache_key = (
            f"users:search:"
            f"{query or 'all'}:"
            f"{page}:"
            f"{page_size}"
        )

        # Meklē Redis kešatmiņā
        cached_result = await self.redis_cache.get(
            cache_key
        )

        if cached_result is not None:
            return UserListResponse.model_validate(
                cached_result
            )

        # Meklē PostgreSQL
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

        response = UserListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            pages=pages,
        )

        # Saglabā Redis
        await self.redis_cache.set(
            cache_key,
            response.model_dump(
                mode="json"
            ),
        )

        return response

    # Lietotāja atjaunošana administratora režīmā
    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:

        try:
            # Administrators nevar atjaunot pats sevi
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

            # Lietotāja lomu atjaunošana
            if data.roles is not None:

                role_names = [
                    role.strip().lower()
                    for role in data.roles
                ]

                if not role_names:
                    raise HTTPException(
                        status_code=400,
                        detail="At least one role is required",
                    )

                role_names = list(
                    dict.fromkeys(
                        role_names
                    )
                )

                roles = (
                    await self.role_repository.get_by_names(
                        role_names
                    )
                )

                found_role_names = {
                    role.name
                    for role in roles
                }

                missing_roles = [
                    role
                    for role in role_names
                    if role not in found_role_names
                ]

                if missing_roles:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            "Roles not found: "
                            + ", ".join(missing_roles)
                        ),
                    )

                role_ids = [
                    role.id
                    for role in roles
                    if role.id is not None
                ]

                await self.user_repository.set_roles(
                    user_id=user.id,
                    role_ids=role_ids,
                )

            # Lietotāja saglabāšana
            user = await self.user_repository.update(
                user
            )

            # Izmaiņu saglabāšana
            await self.user_repository.commit()

            # Dzēš lietotāja kešu
            await self.redis_cache.delete(
                f"user:{user.id}"
            )

            # Notīra meklēšanas kešu
            await self.redis_cache.delete_pattern(
                "users:search:*"
            )

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

            # Paroles pārbaude
            if data.password is not None:

                if data.current_password is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Current password is required",
                    )

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

            # Dzēš lietotāja kešu
            await self.redis_cache.delete(
                f"user:{user.id}"
            )

            # Notīra meklēšanas kešu
            await self.redis_cache.delete_pattern(
                "users:search:*"
            )

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