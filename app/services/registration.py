# ==============================
# Bibliotēku imports
# ==============================

from fastapi import HTTPException

from models import User

from repositories import (
    UserRepository, 
    RoleRepository
)

from schemas.user import (
    UserCreate,
    UserResponse,
)

from utils import (
    DataNormalizer, 
    PasswordManager
)


# ==============================
# Lietotāja reģistrācijas serviss
# ==============================

class RegistrationService:

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        normalizer: DataNormalizer,
        password_manager: PasswordManager,
    ):
        # Lietotāja repozitorijs
        self.user_repository = user_repository

        # Lomu repozitorijs
        self.role_repository = role_repository

        # Datu normalizators
        self.normalizer = normalizer

        # Paroļu pārvaldnieks
        self.password_manager = password_manager

    # Lietotāja reģistrācija
    async def register(
        self,
        data: UserCreate,
    ) -> UserResponse:

        try:
            # Ievaddatu normalizācija
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

            # Pārbauda, vai lietotājvārds jau eksistē
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

            # Pārbauda, vai e-pasts jau eksistē
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

            # Meklē noklusējuma lomu
            role = await self.role_repository.get_by_name(
                "user"
            )

            if role is None:
                raise HTTPException(
                    status_code=500,
                    detail="Default role 'user' not found",
                )

            # Paroles hešošana
            password_hash = (
                self.password_manager.hash_password(
                    data.password
                )
            )

            # Lietotāja objekta izveide
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                password_hash=password_hash,
            )

            # Lietotāja saglabāšana
            user = await self.user_repository.create(
                user
            )

            if user.id is None:
                raise HTTPException(
                    status_code=500,
                    detail="User ID was not generated",
                )

            if role.id is None:
                raise HTTPException(
                    status_code=500,
                    detail="Role ID was not generated",
                )

            # Noklusējuma lomas piešķiršana
            await self.user_repository.add_role(
                user.id,
                role.id,
            )

            # Izmaiņu saglabāšana
            await self.user_repository.commit()

            # Lietotāja lomu iegūšana
            roles = await self.user_repository.get_roles(
                user.id
            )

            # Lietotāja atbildes shēmas izveide
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
            # HTTP kļūdas pārsūtīšana tālāk
            raise

        except Exception:
            # Izmaiņu atcelšana
            await self.user_repository.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to register user",
            )