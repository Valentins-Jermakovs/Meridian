# ==============================
# Library Imports
# ==============================

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
    UserCreate,
    UserResponse,
)

from services import AuditLogService

from utils import (
    DataNormalizer,
    PasswordManager,
)


# ==============================
# User Registration Service
# ==============================

class RegistrationService:
    """
    Provides functionality for registering new users.

    The service normalizes user input, checks username and email
    uniqueness, hashes the user's password, assigns the default
    user role, and records the registration in the audit log.
    """


    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        normalizer: DataNormalizer,
        password_manager: PasswordManager,
    ):
        """
        Initializes the user registration service.

        Args:
            user_repository (UserRepository):
                Repository used to access and manage user data.
            role_repository (RoleRepository):
                Repository used to access user roles.
            normalizer (DataNormalizer):
                Utility used to normalize user input.
            password_manager (PasswordManager):
                Utility used to securely hash user passwords.
        """

        # User repository
        self.user_repository = user_repository

        # Role repository
        self.role_repository = role_repository

        # Data normalizer
        self.normalizer = normalizer

        # Password manager
        self.password_manager = password_manager

        # Audit log service
        self.audit_log_service: AuditLogService | None = None


    # ==============================
    # User Registration
    # ==============================

    async def register(
        self,
        data: UserCreate,
    ) -> UserResponse:
        """
        Registers a new user account.

        The method normalizes the provided user data, checks whether
        the username and email are already registered, hashes the
        password, creates the user, assigns the default user role,
        and returns the created user information.

        Args:
            data (UserCreate): Data required to create a new user.

        Returns:
            UserResponse: Information about the newly registered user.

        Raises:
            HTTPException: If the username or email already exists,
                the default role cannot be found, required IDs are
                missing, or registration fails.
        """

        try:
            # ==============================
            # Normalize Input Data
            # ==============================

            username = (
                self.normalizer.normalize_username(
                    data.username
                )
            )

            email = (
                self.normalizer.normalize_email(
                    str(data.email)
                )
            )

            full_name = (
                self.normalizer.normalize_text(
                    data.full_name
                )
            )

            # ==============================
            # Check Username Uniqueness
            # ==============================

            existing_user = (
                await self.user_repository.get_by_username(
                    username
                )
            )

            if existing_user is not None:

                # Record failed registration
                if self.audit_log_service is not None:
                    await self.audit_log_service.create(
                        user_id=None,
                        action=AuditAction.REGISTER,
                        description=(
                            f"Registration failed: "
                            f"username '{username}' already exists"
                        ),
                        success=False,
                    )

                raise HTTPException(
                    status_code=409,
                    detail="Username already exists",
                )

            # ==============================
            # Check Email Uniqueness
            # ==============================

            existing_user = (
                await self.user_repository.get_by_email(
                    email
                )
            )

            if existing_user is not None:

                # Record failed registration
                if self.audit_log_service is not None:
                    await self.audit_log_service.create(
                        user_id=None,
                        action=AuditAction.REGISTER,
                        description=(
                            f"Registration failed: "
                            f"email '{email}' already exists"
                        ),
                        success=False,
                    )

                raise HTTPException(
                    status_code=409,
                    detail="Email already exists",
                )

            # ==============================
            # Find Default User Role
            # ==============================

            role = await self.role_repository.get_by_name(
                "user"
            )

            if role is None:
                raise HTTPException(
                    status_code=500,
                    detail="Default role 'user' not found",
                )

            # ==============================
            # Hash Password
            # ==============================

            password_hash = (
                self.password_manager.hash_password(
                    data.password
                )
            )

            # ==============================
            # Create User Model
            # ==============================

            user = User(
                username=username,
                full_name=full_name,
                email=email,
                password_hash=password_hash,
            )

            # ==============================
            # Save User
            # ==============================

            user = await self.user_repository.create(
                user
            )

            # ==============================
            # Validate User ID
            # ==============================

            if user.id is None:
                raise HTTPException(
                    status_code=500,
                    detail="User ID was not generated",
                )

            # ==============================
            # Validate Role ID
            # ==============================

            if role.id is None:
                raise HTTPException(
                    status_code=500,
                    detail="Role ID was not generated",
                )

            # ==============================
            # Assign Default User Role
            # ==============================

            await self.user_repository.add_role(
                user.id,
                role.id,
            )

            # ==============================
            # Commit Changes
            # ==============================

            await self.user_repository.commit()

            # ==============================
            # Get User Roles
            # ==============================

            roles = await self.user_repository.get_roles(
                user.id
            )

            # ==============================
            # Record Successful Registration
            # ==============================

            if self.audit_log_service is not None:
                await self.audit_log_service.create(
                    user_id=user.id,
                    action=AuditAction.REGISTER,
                    description=(
                        f"User '{user.username}' "
                        f"successfully registered"
                    ),
                    success=True,
                )

            # ==============================
            # Create User Response
            # ==============================

            return UserResponse(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                email=user.email,
                roles=roles,
                is_active=user.is_active,
                created_at=user.created_at,
            )

        except HTTPException:
            # Re-raise HTTP errors without modification
            raise

        except Exception:
            # Roll back the transaction
            await self.user_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to register user",
            )