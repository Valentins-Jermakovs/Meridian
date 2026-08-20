# ==============================
# Bibliotēku imports
# ==============================

from contextlib import asynccontextmanager

from fastapi import FastAPI

# Datu bāzes inicializācija
from config.database import init_db

# Ceļu imports
from routers import main_router


# ==============================
# Programmas dzīves cikls
# ==============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Datu bāzes inicializācija programmas startēšanas laikā
    await init_db()

    yield


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