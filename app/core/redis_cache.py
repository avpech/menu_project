import redis.asyncio as redis
from redis.asyncio.client import Redis
import json
from fastapi.encoders import jsonable_encoder
from typing import Optional

LIST_PREFIX = "list"
OBJ_PREFIX = "obj"


class RedisCache:

    def __init__(self) -> None:
        self.client: Redis = redis.Redis(decode_responses=True)

    async def disconnect(self):
        await self.client.aclose()

    async def set(self, key, value):
        value = json.dumps(jsonable_encoder(value))
        await self.client.set(key, value, ex=100)

    async def get(self, key):
        value = await self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def invalidate(self, keys: Optional[list[str]] = None, pattern: Optional[str] = None):
        keys_to_delete = []
        if keys is not None:
            keys_to_delete.extend(keys)
        if pattern is not None:
            cur = b"0"
            while cur:
                cur, pattern_keys = await self.client.scan(cur, match=pattern)
            keys_to_delete.extend(pattern_keys)
        await self.client.delete(*keys_to_delete)


cache = RedisCache()
