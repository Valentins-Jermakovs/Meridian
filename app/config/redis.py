# ==============================
# Library imports
# ==============================

import redis.asyncio as redis

from .config import settings


# ==============================
# Redis configuration
# ==============================

# Redis connection string
REDIS_URL = (
    f"redis://"
    f"{settings.REDIS_HOST}:"
    f"{settings.REDIS_PORT}/"
    f"{settings.REDIS_DB}"
)


# ==============================
# Redis client
# ==============================

# Create a Redis client from the connection URL
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


# ==============================
# Redis connection check
# ==============================

async def init_redis():
    """
    This function checks if the Redis connection is working.
    
    Args:
        None
    
    Returns:
        None
    """
    # Ping the Redis server to check the connection
    await redis_client.ping()


# ==============================
# Redis connection closure
# ==============================

async def close_redis():
    """
    This function closes the Redis connection.
    
    Args:
        None
    
    Returns:
        None
    """
    # Close the Redis client
    await redis_client.aclose()