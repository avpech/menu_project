import json
from typing import Any

import redis.asyncio as redis
from fastapi.encoders import jsonable_encoder
from redis.asyncio.client import Redis

from app.core.config import settings

LIST_PREFIX = 'list'
OBJ_PREFIX = 'obj'


class RedisCache:
    """Класс для реализации кеширования с помощью Redis."""

    def __init__(self) -> None:
        self.client: Redis = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True
        )

    async def disconnect(self) -> None:
        """Закрыть соединения."""
        await self.client.close()

    async def clean(self) -> None:
        """Очистить кэш. Для использования при старте сервиса."""
        await self.client.flushdb()

    async def set(self, key: str, value: Any) -> None:
        """Записать в кэш новый ключ `key` со значением `value`."""
        value = json.dumps(jsonable_encoder(value))
        await self.client.set(key, value, ex=settings.cache_lifetime)

    async def get(self, key: str) -> Any:
        """Получить из кэша значение ключа `key`."""
        value = await self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def invalidate(self, keys: list[str] | None = None, pattern: str | None = None) -> None:
        """
        Инвалидировать ключи.

        Удаляет из кэша ключи из списка `keys`, а также ключи,
        соответствущие паттерну `pattern`.
        """
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
