# ==============================
# Library Imports
# ==============================

from contextlib import asynccontextmanager

from fastapi import FastAPI

# Database initialization
from config.database import init_db

from config.redis import (
    init_redis,
    close_redis,
)

# Router imports
from routers import main_router


# ==============================
# Application Lifecycle
# ==============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the FastAPI application lifecycle.

    Initializes the PostgreSQL database and Redis connection
    when the application starts and closes the Redis connection
    when the application shuts down.

    Args:
        app (FastAPI):
            FastAPI application instance.
    """

    # Initialize PostgreSQL
    await init_db()

    # Initialize Redis
    await init_redis()

    yield

    # Close the Redis connection
    await close_redis()


# ==============================
# FastAPI Application
# ==============================

app = FastAPI(
    lifespan=lifespan
)


# ==============================
# Router Registration
# ==============================

app.include_router(
    main_router
)