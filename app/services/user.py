# ==============================
# Bibliotēku imports
# ==============================

from models import User

from repositories.user import UserRepository

from utils.normalizer import DataNormalizer
from utils.password import PasswordManager


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


    # Lietotāju meklēšana ar lapošanu
    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:

        # Lappuses validācija
        if page < 1:
            raise ValueError(
                "Page must be greater than 0"
            )

        # Lapas izmēra validācija
        if page_size < 1:
            raise ValueError(
                "Page size must be greater than 0"
            )

        # Maksimālais rezultātu skaits vienā lapā
        if page_size > 100:
            raise ValueError(
                "Page size cannot exceed 100"
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

        return users, total

    # Lietotāja atjaunošana administratora režīmā
    async def update_by_admin(
        self,
        admin_id: int,
        user_id: int,
        username: str | None = None,
        full_name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        is_active: bool | None = None,
    ) -> User:

        try:
            # Pārbauda, vai administrators nemēģina atjaunot pats sevi
            if admin_id == user_id:
                raise ValueError(
                    "Administrator cannot update themselves"
                )

            # Lietotāja meklēšana
            user = await self.user_repository.get_by_id(
                user_id
            )

            if user is None:
                raise ValueError(
                    "User not found"
                )

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
                        raise ValueError(
                            "Username already exists"
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

                if email != user.email:
                    existing_user = (
                        await self.user_repository.get_by_email(
                            email
                        )
                    )

                    if existing_user is not None:
                        raise ValueError(
                            "Email already exists"
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

            # Lietotāja saglabāšana
            user = await self.user_repository.update(
                user
            )

            # Izmaiņu saglabāšana
            await self.user_repository.commit()

            return user

        except Exception:
            # Izmaiņu atcelšana kļūdas gadījumā
            await self.user_repository.rollback()

            raise

    # Paša lietotāja datu atjaunošana
    async def update_self(
        self,
        user_id: int,
        username: str | None = None,
        full_name: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> User:

        try:
            # Lietotāja meklēšana
            user = await self.user_repository.get_by_id(
                user_id
            )

            if user is None:
                raise ValueError(
                    "User not found"
                )

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
                        raise ValueError(
                            "Username already exists"
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

                if email != user.email:
                    existing_user = (
                        await self.user_repository.get_by_email(
                            email
                        )
                    )

                    if existing_user is not None:
                        raise ValueError(
                            "Email already exists"
                        )

                    user.email = email

            # Paroles atjaunošana
            if password is not None:
                user.password_hash = (
                    self.password_manager.hash_password(
                        password
                    )
                )

            # Lietotāja saglabāšana
            user = await self.user_repository.update(
                user
            )

            # Izmaiņu saglabāšana
            await self.user_repository.commit()

            return user

        except Exception:
            # Izmaiņu atcelšana kļūdas gadījumā
            await self.user_repository.rollback()

            raise