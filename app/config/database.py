# ==============================
# Bibliotēku imports
# ==============================

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

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
# Datu bāzes inicializācija
# ==============================

# Modeļu tabulu izveide datu bāzē
async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(
            SQLModel.metadata.create_all
        )