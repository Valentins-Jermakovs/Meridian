
# ==============================
# Third-party imports
# ==============================

from redis.asyncio import Redis

# ==============================
# Application configuration
# ==============================

from config.config import settings
from utils.redis_cache import RedisCache


# ==============================
# Redis instances
# ==============================

redis_client: Redis | None = None
redis_cache: RedisCache | None = None


# ==============================
# Redis initialization
# ==============================

async def init_redis() -> None:
    """Initialize the shared Redis client and cache."""
    global redis_client, redis_cache

    # Reuse the existing client if Redis is already initialized.
    if redis_client is not None:
        await redis_client.ping()
        return

    client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
        decode_responses=True,
    )

    try:
        # Verify the connection before exposing the client.
        await client.ping()

    except Exception:
        await client.aclose()
        raise

    # Create one shared cache instance for the application.
    redis_client = client
    redis_cache = RedisCache(
        client=client,
        ttl=settings.REDIS_CACHE_TTL,
    )


# ==============================
# Redis dependencies
# ==============================

def get_redis() -> Redis:
    """Return the shared Redis client."""
    if redis_client is None:
        raise RuntimeError("Redis has not been initialized.")

    return redis_client


def get_redis_cache() -> RedisCache:
    """Return the shared Redis cache."""
    if redis_cache is None:
        raise RuntimeError("Redis cache has not been initialized.")

    return redis_cache


# ==============================
# Redis shutdown
# ==============================

async def close_redis() -> None:
    """Close Redis and reset the shared instances."""
    global redis_client, redis_cache

    client = redis_client

    redis_client = None
    redis_cache = None

    if client is not None:
        await client.aclose()
