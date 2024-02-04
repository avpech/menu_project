import json
from typing import Any

import redis.asyncio as redis
from fastapi.encoders import jsonable_encoder
from redis.asyncio.client import Redis

LIST_PREFIX = 'list'
OBJ_PREFIX = 'obj'


class RedisCache:

    def __init__(self) -> None:
        self.client: Redis = redis.Redis(decode_responses=True)

    async def disconnect(self) -> None:
        await self.client.close()

    async def set(self, key: str, value: Any) -> None:
        value = json.dumps(jsonable_encoder(value))
        await self.client.set(key, value, ex=100)

    async def get(self, key: str) -> Any:
        value = await self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def invalidate(self, keys: list[str] | None = None, pattern: str | None = None) -> None:
        keys_to_delete = []
        if keys is not None:
            keys_to_delete.extend(keys)
        if pattern is not None:
            cur: Any = b'0'
            while cur:
                cur, pattern_keys = await self.client.scan(cur, match=pattern)
            keys_to_delete.extend(pattern_keys)
        await self.client.delete(*keys_to_delete)


cache = RedisCache()
