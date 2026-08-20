# Bibliotēkas:
from contextlib import asynccontextmanager
from fastapi import FastAPI
# Datu bāzes inicializators
from config.database import init_db


# Programmas starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# Programmas objekts
app = FastAPI(lifespan=lifespan)

# Testa ceļš
@app.get("/")
async def root():
    return {"message": "Auth service"}