from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .config import settings
import models


DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)


engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(
            SQLModel.metadata.create_all
        )