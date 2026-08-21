# ==============================
# Repository Imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import select

from models import Role


# ==============================
# Role Repository
# ==============================

class RoleRepository:
    """
    A repository for role data storage and retrieval.
    
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

    # Get a role by its name
    async def get_by_name(
        self,
        name: str,
    ) -> Role | None:
        """
        Gets a role by its name.
        
        Args:
            name (str): The name of the role.
        
        Returns:
            Role | None: The role if found, otherwise None.
        """
        result = await self.session.execute(
            select(Role).where(
                Role.name == name
            )
        )

        return result.scalar_one_or_none()

    # Get multiple roles by their names
    async def get_by_names(
        self,
        names: list[str],
    ) -> list[Role]:
        """
        Gets multiple roles by their names.
        
        Args:
            names (list[str]): The list of role names.
        
        Returns:
            list[Role]: The list of roles.
        """
        result = await self.session.execute(
            select(Role).where(
                Role.name.in_(names)
            )
        )

        return list(result.scalars().all())