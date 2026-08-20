# Bibliotēkas:
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.ext.asyncio import create_async_engine
# Iestatījumu imports
from .config import settings


# Pieslēgums DB
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)


# Dziņa izveide
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


# Modeļu inicializācija uz programmas starta
async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)