# ==============================
# Bibliotēku imports
# ==============================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models import Role


# ==============================
# Lomas repozitorijs
# ==============================

class RoleRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        # Datu bāzes sesija
        self.session = session

    # Lomas meklēšana pēc nosaukuma
    async def get_by_name(
        self,
        name: str,
    ) -> Role | None:

        result = await self.session.execute(
            select(Role).where(
                Role.name == name
            )
        )

        return result.scalar_one_or_none()