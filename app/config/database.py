# ==============================
# Library imports
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
# Database configuration
# ==============================

# PostgreSQL connection string
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)


# ==============================
# Database engine
# ==============================

# Asynchronous PostgreSQL engine creation
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
)


# ==============================
# Database session
# ==============================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    This function creates a database session.
    
    Args:
        None
    
    Yields:
        An asynchronous database session.
    """
    async with AsyncSession(
        engine,
        expire_on_commit=False,
    ) as session:
        yield session


# ==============================
# Role initialization
# ==============================

async def init_roles(
    session: AsyncSession,
):
    """
    This function initializes the roles in the database.
    
    Args:
        session (AsyncSession): The current database session.
    
    Returns:
        None
    """
    # Define a list of role data
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

    # Iterate over the role data and check if they exist in the database
    for role_data in roles:
        result = await session.execute(
            select(models.Role).where(
                models.Role.name == role_data["name"]
            )
        )

        role = result.scalar_one_or_none()

        if role is None:
            # If the role does not exist, add it to the database
            session.add(
                models.Role(
                    name=role_data["name"],
                    description=role_data["description"],
                )
            )

    # Commit the changes to the database
    await session.commit()


# ==============================
# Database initialization
# ==============================

async def init_db():
    """
    This function initializes the database.
    
    Args:
        None
    
    Returns:
        None
    """
    # Create the tables in the database
    async with engine.begin() as connection:
        await connection.run_sync(
            SQLModel.metadata.create_all
        )

    # Initialize the roles and data in the database
    async with AsyncSession(
        engine,
        expire_on_commit=False,
    ) as session:
        await init_roles(session)