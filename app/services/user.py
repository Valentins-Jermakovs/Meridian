# ==============================
# Library Imports
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
# User Update Service
# ==============================

class UserUpdateService:
    """
    Provides functionality for retrieving, searching, and updating
    user accounts.

    The service supports both administrator updates and self-service
    profile updates. It also handles role management, password changes,
    Redis caching, and audit logging.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        normalizer: DataNormalizer,
        password_manager: PasswordManager,
        redis_cache: RedisCache,
    ):
        """
        Initializes the user update service.

        Args:
            user_repository (UserRepository):
                Repository used to access and update user data.
            role_repository (RoleRepository):
                Repository used to access and manage user roles.
            normalizer (DataNormalizer):
                Utility used to normalize user input.
            password_manager (PasswordManager):
                Utility used to hash and verify passwords.
            redis_cache (RedisCache):
                Cache used to store frequently requested user data.
        """

        # User repository
        self.user_repository = user_repository

        # Role repository
        self.role_repository = role_repository

        # Data normalizer
        self.normalizer = normalizer

        # Password manager
        self.password_manager = password_manager

        # Redis cache
        self.redis_cache = redis_cache

        # Audit log service
        self.audit_log_service: AuditLogService | None = None

    # ==============================
    # Create Audit Log Entry
    # ==============================

    async def _audit(
        self,
        user_id: int | None,
        action: AuditAction,
        description: str,
        success: bool,
    ) -> None:
        """
        Creates an audit log entry without affecting the main operation.

        Audit logging errors are intentionally ignored so that a failure
        in the audit subsystem does not interrupt the user operation.

        Args:
            user_id (int | None):
                Identifier of the user associated with the action.
            action (AuditAction):
                Type of action being recorded.
            description (str):
                Description of the performed action.
            success (bool):
                Indicates whether the action was successful.
        """

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
            # Audit logging errors must not affect the main operation
            pass

    # ==============================
    # Build User Response
    # ==============================

    async def _build_user_response(
        self,
        user: User,
    ) -> UserResponse:
        """
        Builds a UserResponse object from a user model.

        Args:
            user (User): User model used to build the response.

        Returns:
            UserResponse: Serialized user information including roles.

        Raises:
            HTTPException: If the user does not have a generated ID.
        """

        if user.id is None:
            raise HTTPException(
                status_code=500,
                detail="User ID was not generated",
            )

        # Retrieve the user's roles
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
    # Get User by ID
    # ==============================

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse:
        """
        Retrieves a user by ID.

        The method first checks Redis and only queries PostgreSQL
        when the requested user is not present in the cache.

        Args:
            user_id (int): Identifier of the requested user.

        Returns:
            UserResponse: Requested user information.

        Raises:
            HTTPException: If the user does not exist.
        """

        # Redis cache key
        cache_key = f"user:{user_id}"

        # Check Redis cache
        cached_user = await self.redis_cache.get(
            cache_key
        )

        if cached_user is not None:
            return UserResponse.model_validate(
                cached_user
            )

        # Query PostgreSQL
        user = await self.user_repository.get_by_id(
            user_id
        )

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        # Build response
        response = await self._build_user_response(
            user
        )

        # Store response in Redis
        await self.redis_cache.set(
            cache_key,
            response.model_dump(
                mode="json"
            ),
        )

        return response

    # ==============================
    # Update User Data
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
        """
        Applies the provided changes to a user model.

        Only fields explicitly provided to the method are modified.
        Username and email uniqueness are checked before applying
        corresponding changes.

        Args:
            user (User):
                User model to update.
            username (str | None):
                New username, if provided.
            full_name (str | None):
                New full name, if provided.
            email (str | None):
                New email address, if provided.
            password (str | None):
                New password, if provided.
            is_active (bool | None):
                New account status, if provided.

        Returns:
            User: Updated user model.

        Raises:
            HTTPException: If the new username or email is already used.
        """

        # Update username
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

        # Update full name
        if full_name is not None:

            user.full_name = (
                self.normalizer.normalize_text(
                    full_name
                )
            )

        # Update email
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

        # Update password
        if password is not None:

            user.password_hash = (
                self.password_manager.hash_password(
                    password
                )
            )

        # Update account status
        if is_active is not None:

            user.is_active = is_active

        return user

    # ==============================
    # Search Users with Pagination
    # ==============================

    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> UserListResponse:
        """
        Searches users with pagination and Redis caching.

        Args:
            query (str | None):
                Optional search text.
            page (int):
                Page number starting from 1.
            page_size (int):
                Number of users per page. Maximum value is 100.

        Returns:
            UserListResponse: Paginated list of matching users.

        Raises:
            HTTPException: If the pagination parameters are invalid.
        """

        # Validate page number
        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="Page must be greater than 0",
            )

        # Validate page size
        if page_size < 1:
            raise HTTPException(
                status_code=400,
                detail="Page size must be greater than 0",
            )

        # Limit the maximum page size
        if page_size > 100:
            raise HTTPException(
                status_code=400,
                detail="Page size cannot exceed 100",
            )

        # Normalize search text
        if query is not None:

            query = self.normalizer.normalize_text(
                query
            )

            if not query:
                query = None

        # Redis cache key
        cache_key = (
            f"users:search:"
            f"{query or 'all'}:"
            f"{page}:"
            f"{page_size}"
        )

        # Check Redis cache
        cached_result = await self.redis_cache.get(
            cache_key
        )

        if cached_result is not None:
            return UserListResponse.model_validate(
                cached_result
            )

        # Query PostgreSQL
        users, total = (
            await self.user_repository.search(
                query=query,
                page=page,
                page_size=page_size,
            )
        )

        # Build user list
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

        # Calculate total number of pages
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

        # Store response in Redis
        await self.redis_cache.set(
            cache_key,
            response.model_dump(
                mode="json"
            ),
        )

        return response

    # ==============================
    # Administrator User Update
    # ==============================

    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        data: UserAdminUpdate,
    ) -> UserResponse:
        """
        Updates another user's account using administrator privileges.

        Administrators can update user information, account status,
        password, and roles. An administrator cannot update their
        own account through this method.

        Args:
            admin_id (int):
                Identifier of the administrator performing the update.
            user_id (int):
                Identifier of the user being updated.
            data (UserAdminUpdate):
                User data to update.

        Returns:
            UserResponse: Updated user information.

        Raises:
            HTTPException: If the administrator attempts to update
                themselves, the user does not exist, a role is invalid,
                or the update fails.
        """

        try:
            # ==============================
            # Prevent Self-Administration
            # ==============================

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

            # ==============================
            # Find User
            # ==============================

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

            # Store the original account status
            old_is_active = user.is_active

            # ==============================
            # Update User Data
            # ==============================

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

            # ==============================
            # Update User Roles
            # ==============================

            if data.roles is not None:

                # Normalize role names
                role_names = [
                    role.strip().lower()
                    for role in data.roles
                ]

                # Ensure at least one role is provided
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

                # Remove duplicate role names
                role_names = list(
                    dict.fromkeys(
                        role_names
                    )
                )

                # Find roles in the database
                roles = (
                    await self.role_repository.get_by_names(
                        role_names
                    )
                )

                # Check that all requested roles exist
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

                # Collect IDs of the requested roles
                role_ids = [
                    role.id
                    for role in roles
                    if role.id is not None
                ]

                # Synchronize user roles
                await self.user_repository.set_roles(
                    user_id=user.id,
                    role_ids=role_ids,
                )

            # ==============================
            # Save User
            # ==============================

            user = await self.user_repository.update(
                user
            )

            # Commit changes
            await self.user_repository.commit()

            # ==============================
            # Invalidate User Cache
            # ==============================

            await self.redis_cache.delete(
                f"user:{user.id}"
            )

            # Invalidate user search cache
            await self.redis_cache.delete_pattern(
                "users:search:*"
            )

            # ==============================
            # Record Successful Update
            # ==============================

            await self._audit(
                user_id=admin_id,
                action=AuditAction.ADMIN_UPDATE_USER,
                description=(
                    f"Administrator updated user "
                    f"'{user.username}'"
                ),
                success=True,
            )

            # ==============================
            # Record Role Changes
            # ==============================

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

            # ==============================
            # Record Account Status Changes
            # ==============================

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

            # ==============================
            # Record Password Changes
            # ==============================

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

            # ==============================
            # Build User Response
            # ==============================

            return await self._build_user_response(
                user
            )

        except HTTPException:
            raise

        except Exception:

            # Roll back database changes
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
    # Self User Update
    # ==============================

    async def update_self(
        self,
        user_id: int,
        data: UserSelfUpdate,
    ) -> UserResponse:
        """
        Updates the authenticated user's own profile.

        Users can update their username, full name, email, and password.
        Changing the password requires verification of the current
        password.

        Args:
            user_id (int):
                Identifier of the authenticated user.
            data (UserSelfUpdate):
                User profile fields to update.

        Returns:
            UserResponse: Updated user information.

        Raises:
            HTTPException: If the user does not exist, the current
                password is missing or incorrect, or the update fails.
        """

        try:
            # ==============================
            # Find User
            # ==============================

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

            # ==============================
            # Validate Password Change
            # ==============================

            if data.password is not None:

                # Current password is required
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

                # Verify current password asynchronously
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

            # ==============================
            # Update User Data
            # ==============================

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

            # ==============================
            # Save User
            # ==============================

            user = await self.user_repository.update(
                user
            )

            # Commit changes
            await self.user_repository.commit()

            # ==============================
            # Invalidate User Cache
            # ==============================

            await self.redis_cache.delete(
                f"user:{user.id}"
            )

            # Invalidate user search cache
            await self.redis_cache.delete_pattern(
                "users:search:*"
            )

            # ==============================
            # Record Successful Update
            # ==============================

            await self._audit(
                user_id=user.id,
                action=AuditAction.UPDATE_SELF,
                description=(
                    f"User '{user.username}' "
                    "updated own profile"
                ),
                success=True,
            )

            # ==============================
            # Record Password Change
            # ==============================

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

            # ==============================
            # Build User Response
            # ==============================

            return await self._build_user_response(
                user
            )

        except HTTPException:
            raise

        except Exception:

            # Roll back database changes
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