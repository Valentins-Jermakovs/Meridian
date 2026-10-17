
# ==============================
# Standard library imports
# ==============================

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# ==============================
# Third-party imports
# ==============================

from fastapi import FastAPI

# ==============================
# Application configuration
# ==============================

from config.database import engine, init_db
from config.redis import close_redis, init_redis

# ==============================
# Application routers
# ==============================

from routers import main_router


# ==============================
# Application lifecycle
# ==============================

async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and release application resources."""
    try:
        # Initialize PostgreSQL and Redis.
        await init_db()
        await init_redis()

        yield

    finally:
        # Close Redis and always dispose of the database engine.
        try:
            await close_redis()
        finally:
            await engine.dispose()


# ==============================
# FastAPI application
# ==============================

app = FastAPI(
    title="Meridian",
    lifespan=lifespan,
)

# Register application routes.
app.include_router(main_router)
