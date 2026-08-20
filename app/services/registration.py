# ==============================
# Bibliotēku imports
# ==============================

from models import User

from repositories.user import UserRepository
from repositories.role import RoleRepository

from utils.normalizer import DataNormalizer
from utils.password import PasswordManager


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
        username: str,
        full_name: str,
        email: str,
        password: str,
    ) -> User:

        try:
            # Ievaddatu normalizācija
            username = self.normalizer.normalize_username(
                username
            )

            email = self.normalizer.normalize_email(
                email
            )

            full_name = self.normalizer.normalize_text(
                full_name
            )

            # Pārbauda, vai lietotājvārds jau eksistē
            existing_user = (
                await self.user_repository.get_by_username(
                    username
                )
            )

            if existing_user is not None:
                raise ValueError(
                    "Username already exists"
                )

            # Pārbauda, vai e-pasts jau eksistē
            existing_user = (
                await self.user_repository.get_by_email(
                    email
                )
            )

            if existing_user is not None:
                raise ValueError(
                    "Email already exists"
                )

            # Meklē noklusējuma lomu
            role = await self.role_repository.get_by_name(
                "user"
            )

            if role is None:
                raise ValueError(
                    "Default role 'user' not found"
                )

            # Paroles hešošana
            password_hash = (
                self.password_manager.hash_password(
                    password
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
                raise ValueError(
                    "User ID was not generated"
                )

            if role.id is None:
                raise ValueError(
                    "Role ID was not generated"
                )

            # Lomas piešķiršana
            await self.user_repository.add_role(
                user.id,
                role.id,
            )

            # Izmaiņu saglabāšana
            await self.user_repository.commit()

            return user

        except Exception:
            # Izmaiņu atcelšana kļūdas gadījumā
            await self.user_repository.rollback()

            raise