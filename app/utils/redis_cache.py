# ==============================
# Bibliotēku imports
# ==============================

import json
from typing import Any

import redis.asyncio as redis


# ==============================
# Redis kešatmiņas pārvaldības klase
# ==============================

class RedisCache:

    def __init__(
        self,
        client: redis.Redis,
        ttl: int,
    ):
        # Redis klients
        self.client = client

        # Kešatmiņas dzīves ilgums sekundēs
        self.ttl = ttl

    # Datu iegūšana
    async def get(
        self,
        key: str,
    ) -> Any | None:

        value = await self.client.get(
            key
        )

        if value is None:
            return None

        return json.loads(value)

    # Datu saglabāšana
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:

        await self.client.set(
            key,
            json.dumps(
                value,
                default=str,
            ),
            ex=ttl or self.ttl,
        )

    # Datu dzēšana
    async def delete(
        self,
        key: str,
    ) -> None:

        await self.client.delete(
            key
        )

    # Pārbaude, vai atslēga eksistē
    async def exists(
        self,
        key: str,
    ) -> bool:

        return bool(
            await self.client.exists(
                key
            )
        )

    # Atslēgu dzēšana pēc šablona
    async def delete_pattern(
        self,
        pattern: str,
    ) -> None:

        keys = []

        async for key in self.client.scan_iter(
            match=pattern
        ):
            keys.append(key)

        if keys:
            await self.client.delete(
                *keys
            )