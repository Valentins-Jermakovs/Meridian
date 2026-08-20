# ==============================
# Bibliotēku imports
# ==============================

from math import ceil

from fastapi import HTTPException

from models import (
    AuditAction,
    User,
)

from repositories import (
    RoleRepository,
    UserRepository,
)

from schemas.user import (
    UserAdminUpdate,
    UserListItem,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
)

from services import AuditLogService

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

        # Audit žurnāla serviss
        self.audit_log_service: AuditLogService | None = None

    # ==============================
    # Audit ieraksta izveide
    # ==============================

    async def _audit(
        self,
        user_id: int | None,
        action: AuditAction,
        description: str,
        success: bool,
    ) -> None:

        if self.audit_log_service is None:
            return

        try:
            await self.audit_log_service.create(
                user_id=user_id,
                action=action,
                description=description,
                success=success,
            )

        except Exception:
            # Audit kļūda nedrīkst ietekmēt
            # galveno lietotāja darbību
            pass

    # ==============================
    # Lietotāja atbildes shēmas izveide
    # ==============================

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

    # ==============================
    # Lietotāja meklēšana pēc ID
    # ==============================

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

    # ==============================
    # Lietotāja datu atjaunošana
    # ==============================

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

    # ==============================
    # Lietotāju meklēšana ar lapošanu
    # ==============================

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

        # Maksimālais lietotāju skaits vienā lapā
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

    # ==============================
    # Lietotāja atjaunošana
    # administratora režīmā
    # ==============================

    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:

        try:
            # Administrators nevar atjaunot pats sevi
            if admin_id == user_id:

                await self._audit(
                    user_id=admin_id,
                    action=AuditAction.ADMIN_UPDATE_USER,
                    description=(
                        "Administrator update failed: "
                        "administrator cannot update themselves"
                    ),
                    success=False,
                )

                raise HTTPException(
                    status_code=403,
                    detail="Administrator cannot update themselves",
                )

            # Lietotāja meklēšana
            user = await self.user_repository.get_by_id(
                user_id
            )

            if user is None:

                await self._audit(
                    user_id=admin_id,
                    action=AuditAction.ADMIN_UPDATE_USER,
                    description=(
                        f"Administrator update failed: "
                        f"user with ID {user_id} not found"
                    ),
                    success=False,
                )

                raise HTTPException(
                    status_code=404,
                    detail="User not found",
                )

            # Lietotāja sākotnējais statuss
            old_is_active = user.is_active

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

                # Normalizē lomu nosaukumus
                role_names = [
                    role.strip().lower()
                    for role in data.roles
                ]

                # Pārbauda, vai nav tukšas lomas
                if not role_names:

                    await self._audit(
                        user_id=admin_id,
                        action=AuditAction.CHANGE_ROLE,
                        description=(
                            f"Role update failed for "
                            f"user '{user.username}': "
                            "at least one role is required"
                        ),
                        success=False,
                    )

                    raise HTTPException(
                        status_code=400,
                        detail="At least one role is required",
                    )

                # Noņem dublikātus
                role_names = list(
                    dict.fromkeys(
                        role_names
                    )
                )

                # Atrod lomas datu bāzē
                roles = (
                    await self.role_repository.get_by_names(
                        role_names
                    )
                )

                # Pārbauda, vai visas lomas eksistē
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

                    await self._audit(
                        user_id=admin_id,
                        action=AuditAction.CHANGE_ROLE,
                        description=(
                            f"Role update failed for "
                            f"user '{user.username}': "
                            f"roles not found: "
                            f"{', '.join(missing_roles)}"
                        ),
                        success=False,
                    )

                    raise HTTPException(
                        status_code=404,
                        detail=(
                            "Roles not found: "
                            + ", ".join(missing_roles)
                        ),
                    )

                # ID atrastajām lomām
                role_ids = [
                    role.id
                    for role in roles
                    if role.id is not None
                ]

                # Lomu sinhronizācija
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

            # Veiksmīgs administratora atjauninājums
            await self._audit(
                user_id=admin_id,
                action=AuditAction.ADMIN_UPDATE_USER,
                description=(
                    f"Administrator updated user "
                    f"'{user.username}'"
                ),
                success=True,
            )

            # Lomu maiņas ieraksts
            if data.roles is not None:

                await self._audit(
                    user_id=admin_id,
                    action=AuditAction.CHANGE_ROLE,
                    description=(
                        f"Administrator changed roles "
                        f"for user '{user.username}'"
                    ),
                    success=True,
                )

            # Konta statusa maiņas ieraksts
            if (
                data.is_active is not None
                and old_is_active != user.is_active
            ):

                action = (
                    AuditAction.ACCOUNT_ACTIVATED
                    if user.is_active
                    else AuditAction.ACCOUNT_DEACTIVATED
                )

                await self._audit(
                    user_id=admin_id,
                    action=action,
                    description=(
                        f"Administrator changed account "
                        f"status for user "
                        f"'{user.username}'"
                    ),
                    success=True,
                )

            # Paroles maiņas ieraksts
            if data.password is not None:

                await self._audit(
                    user_id=admin_id,
                    action=AuditAction.CHANGE_PASSWORD,
                    description=(
                        f"Administrator changed password "
                        f"for user '{user.username}'"
                    ),
                    success=True,
                )

            # Lietotāja atbildes izveide
            return await self._build_user_response(
                user
            )

        except HTTPException:
            raise

        except Exception:

            await self.user_repository.rollback()

            await self._audit(
                user_id=admin_id,
                action=AuditAction.ADMIN_UPDATE_USER,
                description=(
                    "Administrator update failed "
                    "because of an unexpected error"
                ),
                success=False,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to update user",
            )

    # ==============================
    # Paša lietotāja datu atjaunošana
    # ==============================

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

                await self._audit(
                    user_id=user_id,
                    action=AuditAction.UPDATE_SELF,
                    description=(
                        "User update failed: "
                        "user not found"
                    ),
                    success=False,
                )

                raise HTTPException(
                    status_code=404,
                    detail="User not found",
                )

            # Paroles pārbaude
            if data.password is not None:

                # Pašreizējā parole nav norādīta
                if data.current_password is None:

                    await self._audit(
                        user_id=user.id,
                        action=AuditAction.UPDATE_SELF,
                        description=(
                            f"User '{user.username}' "
                            "update failed: "
                            "current password is required"
                        ),
                        success=False,
                    )

                    raise HTTPException(
                        status_code=400,
                        detail="Current password is required",
                    )

                # Pašreizējā parole
                # tiek pārbaudīta asinhroni
                password_valid = (
                    await self.password_manager.verify_password(
                        data.current_password,
                        user.password_hash,
                    )
                )

                if not password_valid:

                    await self._audit(
                        user_id=user.id,
                        action=AuditAction.UPDATE_SELF,
                        description=(
                            f"User '{user.username}' "
                            "update failed: "
                            "current password is incorrect"
                        ),
                        success=False,
                    )

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

            # Veiksmīgs atjauninājums
            await self._audit(
                user_id=user.id,
                action=AuditAction.UPDATE_SELF,
                description=(
                    f"User '{user.username}' "
                    "updated own profile"
                ),
                success=True,
            )

            # Paroles maiņas ieraksts
            if data.password is not None:

                await self._audit(
                    user_id=user.id,
                    action=AuditAction.CHANGE_PASSWORD,
                    description=(
                        f"User '{user.username}' "
                        "changed own password"
                    ),
                    success=True,
                )

            # Lietotāja atbildes izveide
            return await self._build_user_response(
                user
            )

        except HTTPException:
            raise

        except Exception:

            await self.user_repository.rollback()

            await self._audit(
                user_id=user_id,
                action=AuditAction.UPDATE_SELF,
                description=(
                    "User update failed "
                    "because of an unexpected error"
                ),
                success=False,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to update user",
            )