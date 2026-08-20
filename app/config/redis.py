# ==============================
# Bibliotēku imports
# ==============================

import redis.asyncio as redis

from .config import settings


# ==============================
# Redis konfigurācija
# ==============================

REDIS_URL = (
    f"redis://"
    f"{settings.REDIS_HOST}:"
    f"{settings.REDIS_PORT}/"
    f"{settings.REDIS_DB}"
)


# ==============================
# Redis klients
# ==============================

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


# ==============================
# Redis savienojuma pārbaude
# ==============================

async def init_redis():
    await redis_client.ping()


# ==============================
# Redis savienojuma aizvēršana
# ==============================

async def close_redis():
    await redis_client.aclose()