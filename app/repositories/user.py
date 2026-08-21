# ==============================
# Repository Imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import (
    delete, 
    func, 
    or_, 
    select
)

from models import (
    User,
    UserRole,
    Role,
)


# ==============================
# UserRepository
# ==============================

class UserRepository:
    """
    A repository for user data storage and retrieval.
    
    Attributes:
        session (AsyncSession): The asynchronous database session.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        """
        Initializes the repository with an asynchronous database session.
        
        Args:
            session (AsyncSession): The asynchronous database session.
        """
        # Datu bāzes sesija
        self.session = session

    # ==============================
    # Commit Changes to Database
    # ==============================

    async def commit(self):
        """
        Commits the changes to the database.
        """
        await self.session.commit()

    # ==============================
    # Rollback Changes to Database
    # ==============================

    async def rollback(self):
        """
        Rolls back the changes to the database.
        """
        await self.session.rollback()

    # ==============================
    # Search Users
    # ==============================

    async def search(
        self,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        """
        Searches users by their username, email, or full name.
        
        Args:
            query (str | None): The search query. Defaults to None.
            page (int): The page number. Defaults to 1.
            page_size (int): The page size. Defaults to 20.
        
        Returns:
            tuple[list[User], int]: A tuple containing the list of users and the total count.
        """
        offset = (
            (page - 1)
            * page_size
        )

        statement = select(
            User
        )

        if query:
            search_query = (
                f"%{query.strip()}%"
            )

            statement = statement.where(
                User.username.ilike(
                    search_query
                )
                | User.full_name.ilike(
                    search_query
                )
                | User.email.ilike(
                    search_query
                )
            )

        count_statement = select(
            func.count()
        ).select_from(
            statement.subquery()
        )

        total_result = (
            await self.session.execute(
                count_statement
            )
        )

        total = (
            total_result.scalar_one()
        )

        statement = (
            statement
            .order_by(User.id)
            .offset(offset)
            .limit(page_size)
        )

        result = (
            await self.session.execute(
                statement
            )
        )

        users = list(
            result.scalars().all()
        )

        return users, total

    # ==============================
    # Get User by ID
    # ==============================

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        """
        Gets a user by their ID.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            User | None: The user if found, otherwise None.
        """
        result = (
            await self.session.execute(
                select(User).where(
                    User.id == user_id
                )
            )
        )

        return result.scalar_one_or_none()

    # ==============================
    # Get User by Login
    # ==============================

    async def get_by_login(
        self,
        login: str,
    ) -> User | None:
        """
        Gets a user by their username or email.
        
        Args:
            login (str): The username or email of the user.
        
        Returns:
            User | None: The user if found, otherwise None.
        """
        result = (
            await self.session.execute(
                select(User).where(
                    or_(
                        User.username == login,
                        User.email == login,
                    )
                )
            )
        )

        return result.scalar_one_or_none()

    # ==============================
    # Get User by Email
    # ==============================

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        """
        Gets a user by their email.
        
        Args:
            email (str): The email of the user.
        
        Returns:
            User | None: The user if found, otherwise None.
        """
        result = (
            await self.session.execute(
                select(User).where(
                    User.email == email
                )
            )
        )

        return result.scalar_one_or_none()

    # ==============================
    # Get User by Username
    # ==============================

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        """
        Gets a user by their username.
        
        Args:
            username (str): The username of the user.
        
        Returns:
            User | None: The user if found, otherwise None.
        """
        result = (
            await self.session.execute(
                select(User).where(
                    User.username == username
                )
            )
        )

        return result.scalar_one_or_none()

    # ==============================
    # Get Roles of a User
    # ==============================

    async def get_roles(
        self,
        user_id: int,
    ) -> list[str]:
        """
        Gets the roles of a user.
        
        Args:
            user_id (int): The ID of the user.
        
        Returns:
            list[str]: The list of role names.
        """
        result = (
            await self.session.execute(
                select(Role.name)
                .join(
                    UserRole,
                    Role.id == UserRole.role_id,
                )
                .where(
                    UserRole.user_id == user_id
                )
            )
        )

        return list(
            result.scalars().all()
        )

    # ==============================
    # Create a User
    # ==============================

    async def create(
        self,
        user: User,
    ) -> User:
        """
        Creates a new user.
        
        Args:
            user (User): The user to be created.
        
        Returns:
            User: The newly created user.
        """
        self.session.add(
            user
        )

        await self.session.flush()
        await self.session.refresh(
            user
        )

        return user

    # ==============================
    # Update a User
    # ==============================

    async def update(
        self,
        user: User,
    ) -> User:
        """
        Updates an existing user.
        
        Args:
            user (User): The user to be updated.
        
        Returns:
            User: The updated user.
        """
        self.session.add(
            user
        )

        await self.session.flush()
        await self.session.refresh(
            user
        )

        return user

    # ==============================
    # Add Role to a User
    # ==============================

    async def add_role(
        self,
        user_id: int,
        role_id: int,
    ) -> UserRole:
        """
        Adds a role to a user.
        
        Args:
            user_id (int): The ID of the user.
            role_id (int): The ID of the role.
        
        Returns:
            UserRole: The newly created user-role relationship.
        """
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
        )

        self.session.add(
            user_role
        )

        await self.session.flush()

        return user_role

    # ==============================
    # Set Roles of a User
    # ==============================

    async def set_roles(
        self,
        user_id: int,
        role_ids: list[int],
    ) -> None:
        """
        Sets the roles of a user.
        
        Args:
            user_id (int): The ID of the user.
            role_ids (list[int]): The list of role IDs.
        """
        # Esošo lomu dzēšana
        await self.session.execute(
            delete(UserRole).where(
                UserRole.user_id == user_id
            )
        )

        # Jauno lomu pievienošana
        for role_id in role_ids:
            self.session.add(
                UserRole(
                    user_id=user_id,
                    role_id=role_id,
                )
            )

        await self.session.flush()