# ==============================
# Bibliotēku imports
# ==============================

from contextlib import asynccontextmanager

from fastapi import FastAPI

# Datu bāzes inicializācija
from config.database import init_db


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
# Testa maršruts
# ==============================

@app.get("/")
async def root():
    return {"message": "Auth service"}