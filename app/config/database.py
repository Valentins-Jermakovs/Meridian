# ==============================
# Bibliotēku imports
# ==============================

from collections.abc import AsyncGenerator

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from .config import settings

import models


# ==============================
# Datu bāzes konfigurācija
# ==============================

# PostgreSQL savienojuma adrese
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)


# ==============================
# Datu bāzes dzinējs
# ==============================

# Asinhronā PostgreSQL dzinēja izveide
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


# ==============================
# Datu bāzes sesija
# ==============================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


# ==============================
# Sākotnējo lomu inicializācija
# ==============================

async def init_roles(
    session: AsyncSession,
):
    roles = [
        {
            "name": "admin",
            "description": "System administrator",
        },
        {
            "name": "user",
            "description": "Standard user",
        },
    ]

    for role_data in roles:
        result = await session.execute(
            select(models.Role).where(
                models.Role.name == role_data["name"]
            )
        )

        role = result.scalar_one_or_none()

        if role is None:
            session.add(
                models.Role(
                    name=role_data["name"],
                    description=role_data["description"],
                )
            )

    await session.commit()


# ==============================
# Datu bāzes inicializācija
# ==============================

async def init_db():
    # Tabulu izveide
    async with engine.begin() as connection:
        await connection.run_sync(
            SQLModel.metadata.create_all
        )

    # Sākotnējo datu izveide
    async with AsyncSession(engine) as session:
        await init_roles(session)