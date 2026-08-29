# ==============================
# Library Imports
# ==============================

import json
from typing import Any

import redis.asyncio as redis


# ==============================
# Redis Cache Management
# ==============================

class RedisCache:
    """
    Provides asynchronous operations for storing, retrieving,
    checking, and deleting data in Redis.

    Values are serialized to JSON before being stored and
    deserialized when retrieved.
    """


    def __init__(
        self,
        client: redis.Redis,
        ttl: int,
    ):
        """
        Initializes the Redis cache manager.

        Args:
            client (redis.Redis):
                Asynchronous Redis client used for cache operations.
            ttl (int):
                Default cache lifetime in seconds.
        """

        # Redis client
        self.client = client

        # Default cache lifetime in seconds
        self.ttl = ttl


    # ==============================
    # Get Cached Data
    # ==============================

    async def get(
        self,
        key: str,
    ) -> Any | None:
        """
        Retrieves a value from Redis by its key.

        The stored JSON value is deserialized back into a Python object.

        Args:
            key (str):
                Redis key used to identify the cached value.

        Returns:
            Any | None:
                Deserialized cached value, or None if the key does not exist.
        """

        value = await self.client.get(
            key
        )

        # Return None when the key does not exist
        if value is None:
            return None

        # Deserialize the stored JSON value
        return json.loads(value)


    # ==============================
    # Set Cached Data
    # ==============================

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """
        Stores a value in Redis with an expiration time.

        Args:
            key (str):
                Redis key used to identify the cached value.
            value (Any):
                Value to store in the cache.
            ttl (int | None):
                Cache lifetime in seconds. If not provided,
                the default TTL is used.
        """

        await self.client.set(
            key,
            json.dumps(
                value,
                default=str,
            ),
            ex=ttl or self.ttl,
        )


    # ==============================
    # Delete Cached Data
    # ==============================

    async def delete(
        self,
        key: str,
    ) -> None:
        """
        Deletes a cached value from Redis.

        Args:
            key (str):
                Redis key to delete.
        """

        await self.client.delete(
            key
        )


    # ==============================
    # Check Key Existence
    # ==============================

    async def exists(
        self,
        key: str,
    ) -> bool:
        """
        Checks whether a key exists in Redis.

        Args:
            key (str):
                Redis key to check.

        Returns:
            bool:
                True if the key exists, otherwise False.
        """

        return bool(
            await self.client.exists(
                key
            )
        )


    # ==============================
    # Delete Keys by Pattern
    # ==============================

    async def delete_pattern(
        self,
        pattern: str,
    ) -> None:
        """
        Deletes all Redis keys matching a specified pattern.

        The SCAN operation is used to iterate over matching keys
        without blocking Redis with a full keyspace scan.

        Args:
            pattern (str):
                Redis key pattern used to find keys for deletion.
        """

        keys = []

        # Find matching keys using the non-blocking SCAN operation
        async for key in self.client.scan_iter(
            match=pattern
        ):
            keys.append(key)

        # Delete all matching keys if any were found
        if keys:
            await self.client.delete(
                *keys
            )