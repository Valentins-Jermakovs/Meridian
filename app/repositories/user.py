# ==============================
# Bibliotēku imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from models import User, UserRole, Role


# ==============================
# Lietotāja repozitorijs
# ==============================

class UserRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        # Datu bāzes sesija
        self.session = session

    # Izmaiņu saglabāšana datu bāzē
    async def commit(self):
        await self.session.commit()

    # Izmaiņu atcelšana datu bāzē
    async def rollback(self):
        await self.session.rollback()

    # Lietotāju meklēšana

    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:

        offset = (page - 1) * page_size

        statement = select(User)

        if query:
            search_query = f"%{query.strip()}%"

            statement = statement.where(
                User.username.ilike(search_query)
                | User.full_name.ilike(search_query)
                | User.email.ilike(search_query)
            )

        count_statement = select(
            func.count()
        ).select_from(
            statement.subquery()
        )

        total_result = await self.session.execute(
            count_statement
        )

        total = total_result.scalar_one()

        statement = (
            statement
            .order_by(User.id)
            .offset(offset)
            .limit(page_size)
        )

        result = await self.session.execute(
            statement
        )

        users = list(result.scalars().all())

        return users, total

    # Lietotāja meklēšana pēc ID
    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:

        result = await self.session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()

    # Lietotāja meklēšana pēc e-pasta
    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        result = await self.session.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    # Lietotāja meklēšana pēc lietotājvārda
    async def get_by_username(
        self,
        username: str,
    ) -> User | None:

        result = await self.session.execute(
            select(User).where(
                User.username == username
            )
        )

        return result.scalar_one_or_none()

    # Lietotāja lomu iegūšana
    async def get_roles(
        self,
        user_id: int,
    ) -> list[str]:

        result = await self.session.execute(
            select(Role.name)
            .join(
                UserRole,
                Role.id == UserRole.role_id,
            )
            .where(
                UserRole.user_id == user_id
            )
        )

        return list(result.scalars().all())

    # Lietotāja izveide
    async def create(
        self,
        user: User,
    ) -> User:

        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    # Lietotāja atjaunošana
    async def update(
        self,
        user: User,
    ) -> User:

        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    # Lomas piešķiršana lietotājam
    async def add_role(
        self,
        user_id: int,
        role_id: int,
    ) -> UserRole:

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
        )

        self.session.add(user_role)

        await self.session.flush()

        return user_role
