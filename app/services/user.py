
# ==============================
# Standard library imports
# ==============================

from datetime import datetime
from math import ceil

# ==============================
# Third-party imports
# ==============================

from fastapi import HTTPException

# ==============================
# Application configuration
# ==============================

from config.redis import get_redis_cache

# ==============================
# Application models
# ==============================

from models import (
    AuditAction,
    User,
)

# ==============================
# Application repositories
# ==============================

from repositories import (
    RoleRepository,
    UserRepository,
)

# ==============================
# Application schemas
# ==============================

from schemas import (
    UserAdminUpdate,
    UserListItem,
    UserListResponse,
    UserRegistrationStatisticItem,
    UserRegistrationStatisticsResponse,
    UserResponse,
    UserSelfUpdate,
    UserStatisticsResponse,
)

# ==============================
# Application services
# ==============================

from services import AuditLogService

# ==============================
# Application utilities
# ==============================

from utils import (
    DataNormalizer,
    PasswordManager,
)


# ==============================
# User update service
# ==============================

class UserUpdateService:
    """Manage user profiles, roles, caching, statistics, and audit logging."""

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        normalizer: DataNormalizer,
        password_manager: PasswordManager,
    ) -> None:
        """Initialize the user update service."""

        # Repository dependencies.
        self.user_repository = user_repository
        self.role_repository = role_repository

        # Utility dependencies.
        self.normalizer = normalizer
        self.password_manager = password_manager

        # Use the shared Redis cache.
        self.redis_cache = get_redis_cache()

        # The facade connects the audit logging service.
        self.audit_log_service: AuditLogService | None = None

    # ==============================
    # Create audit log entry
    # ==============================

    async def _audit(
        self,
        user_id: int | None,
        action: AuditAction,
        description: str,
        success: bool,
    ) -> None:
        """Record an audit event without interrupting the main operation."""
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
            pass

    # ==============================
    # Build user response
    # ==============================

    async def _build_user_response(
        self,
        user: User,
    ) -> UserResponse:
        """Build a user response including assigned roles."""
        if user.id is None:
            raise HTTPException(
                status_code=500,
                detail="User ID was not generated",
            )

        roles = await self.user_repository.get_roles(user.id)

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
    # Get user by ID
    # ==============================

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse:
        """Return a user by ID, using Redis when available."""
        cache_key = f"user:{user_id}"

        # Check the shared Redis cache.
        cached_user = await self.redis_cache.get(cache_key)

        if cached_user is not None:
            return UserResponse.model_validate(cached_user)

        # Query PostgreSQL on a cache miss.
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        response = await self._build_user_response(user)

        # Cache the response.
        await self.redis_cache.set(
            cache_key,
            response.model_dump(mode="json"),
        )

        return response

    # ==============================
    # Update user data
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
        """Apply validated changes to a user model."""

        # Update username.
        if username is not None:
            username = self.normalizer.normalize_username(username)

            if username != user.username:
                existing_user = (
                    await self.user_repository.get_by_username(username)
                )

                if existing_user is not None:
                    raise HTTPException(
                        status_code=409,
                        detail="Username already exists",
                    )

                user.username = username

        # Update full name.
        if full_name is not None:
            user.full_name = self.normalizer.normalize_text(full_name)

        # Update email.
        if email is not None:
            email = self.normalizer.normalize_email(email)

            if email != str(user.email):
                existing_user = (
                    await self.user_repository.get_by_email(email)
                )

                if existing_user is not None:
                    raise HTTPException(
                        status_code=409,
                        detail="Email already exists",
                    )

                user.email = email

        # Update password.
        if password is not None:
            user.password_hash = self.password_manager.hash_password(
                password
            )

        # Update account status.
        if is_active is not None:
            user.is_active = is_active

        return user

    # ==============================
    # Search users with pagination
    # ==============================

    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> UserListResponse:
        """Search users with pagination and Redis caching."""

        # Validate pagination parameters.
        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="Page must be greater than 0",
            )

        if page_size < 1:
            raise HTTPException(
                status_code=400,
                detail="Page size must be greater than 0",
            )

        if page_size > 100:
            raise HTTPException(
                status_code=400,
                detail="Page size cannot exceed 100",
            )

        # Normalize search text.
        if query is not None:
            query = self.normalizer.normalize_text(query)

            if not query:
                query = None

        # Build a cache key from the search parameters.
        cache_key = (
            f"users:search:"
            f"{query or 'all'}:"
            f"{page}:"
            f"{page_size}"
        )

        # Check Redis before querying PostgreSQL.
        cached_result = await self.redis_cache.get(cache_key)

        if cached_result is not None:
            return UserListResponse.model_validate(cached_result)

        # Query PostgreSQL.
        users, total = await self.user_repository.search(
            query=query,
            page=page,
            page_size=page_size,
        )

        # Build the response items.
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

        response = UserListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            pages=ceil(total / page_size),
        )

        # Cache the paginated result.
        await self.redis_cache.set(
            cache_key,
            response.model_dump(mode="json"),
        )

        return response

    # ==============================
    # Administrator user update
    # ==============================

    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:
        """Update a user account using administrator privileges."""
        try:
            # Prevent administrators from updating their own account.
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

            # Find the target user.
            user = await self.user_repository.get_by_id(user_id)

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

            old_is_active = user.is_active

            # Update the user's basic information.
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

            # Update user roles when requested.
            if data.roles is not None:
                role_names = [
                    role.strip().lower()
                    for role in data.roles
                ]

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

                role_names = list(dict.fromkeys(role_names))

                roles = await self.role_repository.get_by_names(
                    role_names
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

                role_ids = [
                    role.id
                    for role in roles
                    if role.id is not None
                ]

                await self.user_repository.set_roles(
                    user_id=user.id,
                    role_ids=role_ids,
                )

            # Save the updated user.
            user = await self.user_repository.update(user)
            await self.user_repository.commit()

            # Invalidate cached user data and searches.
            await self.redis_cache.delete(f"user:{user.id}")
            await self.redis_cache.delete_pattern("users:search:*")

            # Invalidate statistics when the account status changes.
            if (
                data.is_active is not None
                and old_is_active != user.is_active
            ):
                await self.redis_cache.delete("users:statistics")

            # Record the successful update.
            await self._audit(
                user_id=admin_id,
                action=AuditAction.ADMIN_UPDATE_USER,
                description=(
                    f"Administrator updated user "
                    f"'{user.username}'"
                ),
                success=True,
            )

            # Record role changes.
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

            # Record account status changes.
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
                        f"status for user '{user.username}'"
                    ),
                    success=True,
                )

            # Record password changes.
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

            return await self._build_user_response(user)

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
            ) from None

    # ==============================
    # Self profile update
    # ==============================

    async def update_self(
        self,
        user_id: int,
        data: UserSelfUpdate,
    ) -> UserResponse:
        """Update the authenticated user's own profile."""
        try:
            # Find the current user.
            user = await self.user_repository.get_by_id(user_id)

            if user is None:
                await self._audit(
                    user_id=user_id,
                    action=AuditAction.UPDATE_SELF,
                    description="User update failed: user not found",
                    success=False,
                )

                raise HTTPException(
                    status_code=404,
                    detail="User not found",
                )

            # Verify the current password when changing the password.
            if data.password is not None:
                if data.current_password is None:
                    await self._audit(
                        user_id=user.id,
                        action=AuditAction.UPDATE_SELF,
                        description=(
                            f"User '{user.username}' update failed: "
                            "current password is required"
                        ),
                        success=False,
                    )

                    raise HTTPException(
                        status_code=400,
                        detail="Current password is required",
                    )

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
                            f"User '{user.username}' update failed: "
                            "current password is incorrect"
                        ),
                        success=False,
                    )

                    raise HTTPException(
                        status_code=401,
                        detail="Current password is incorrect",
                    )

            # Update the user's profile.
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

            # Save the updated user.
            user = await self.user_repository.update(user)
            await self.user_repository.commit()

            # Invalidate cached user data and searches.
            await self.redis_cache.delete(f"user:{user.id}")
            await self.redis_cache.delete_pattern("users:search:*")

            # Record the successful update.
            await self._audit(
                user_id=user.id,
                action=AuditAction.UPDATE_SELF,
                description=(
                    f"User '{user.username}' updated own profile"
                ),
                success=True,
            )

            # Record password changes.
            if data.password is not None:
                await self._audit(
                    user_id=user.id,
                    action=AuditAction.CHANGE_PASSWORD,
                    description=(
                        f"User '{user.username}' changed own password"
                    ),
                    success=True,
                )

            return await self._build_user_response(user)

        except HTTPException:
            raise

        except Exception:
            await self.user_repository.rollback()

            await self._audit(
                user_id=user_id,
                action=AuditAction.UPDATE_SELF,
                description=(
                    "User update failed because of an unexpected error"
                ),
                success=False,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to update user",
            ) from None

    # ==============================
    # User statistics
    # ==============================

    async def get_statistics(self) -> UserStatisticsResponse:
        """Return total, active, and blocked user statistics."""
        cache_key = "users:statistics"

        # Check Redis before querying PostgreSQL.
        cached_result = await self.redis_cache.get(cache_key)

        if cached_result is not None:
            return UserStatisticsResponse.model_validate(cached_result)

        # Query PostgreSQL.
        statistics = await self.user_repository.get_statistics()

        response = UserStatisticsResponse(
            total=statistics["total"],
            active=statistics["active"],
            blocked=statistics["blocked"],
        )

        # Cache statistics for a short period.
        await self.redis_cache.set(
            cache_key,
            response.model_dump(mode="json"),
            ttl=30,
        )

        return response

    # ==============================
    # User registration statistics
    # ==============================

    async def get_registration_statistics(
        self,
        year: int | None = None,
    ) -> UserRegistrationStatisticsResponse:
        """Return monthly user registration statistics."""
        # Use the current year when none is specified.
        if year is None:
            year = datetime.now().year

        cache_key = f"users:registrations:{year}"

        # Check Redis before querying PostgreSQL.
        cached_result = await self.redis_cache.get(cache_key)

        if cached_result is not None:
            return UserRegistrationStatisticsResponse.model_validate(
                cached_result
            )

        # Query PostgreSQL.
        statistics = (
            await self.user_repository.get_registration_statistics(
                year=year,
            )
        )

        items = [
            UserRegistrationStatisticItem(
                month=item["month"],
                registrations=item["registrations"],
            )
            for item in statistics
        ]

        response = UserRegistrationStatisticsResponse(
            year=year,
            items=items,
        )

        # Cache the result for five minutes.
        await self.redis_cache.set(
            cache_key,
            response.model_dump(mode="json"),
            ttl=300,
        )

        return response
