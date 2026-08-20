# ==============================
# Bibliotēku imports
# ==============================

from contextlib import asynccontextmanager

from fastapi import FastAPI

# Datu bāzes inicializācija
from config.database import init_db

from config.redis import (
    init_redis,
    close_redis,
)

# Ceļu imports
from routers import main_router


# ==============================
# Programmas dzīves cikls
# ==============================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # PostgreSQL inicializācija
    await init_db()

    # Redis inicializācija
    await init_redis()

    yield

    # Redis savienojuma aizvēršana
    await close_redis()


# ==============================
# FastAPI aplikācijas objekts
# ==============================

app = FastAPI(
    lifespan=lifespan
)


# ==============================
# Maršruti
# ==============================

app.include_router(
    main_router
)