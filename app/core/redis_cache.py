import json
import uuid
from typing import Any

import redis.asyncio as redis
from fastapi.encoders import jsonable_encoder
from redis.asyncio.client import Redis

from app.core.config import settings

LIST_PREFIX = 'list'
OBJ_PREFIX = 'obj'
ALL_NESTED_PREFIX = 'all_nested'
DISCOUNT_PREFIX = 'discount'


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

    async def set(self, key: str, value: Any, lifetime: bool = True) -> None:
        """
        Записать в кэш новый ключ `key` со значением `value`.

        Если `lifetime` имеет значение `False`, то кэш устанавливается бессрочно.
        """
        ex = settings.cache_lifetime if lifetime else None
        value = json.dumps(jsonable_encoder(value))
        await self.client.set(key, value, ex=ex)

    async def get(self, key: str) -> Any:
        """Получить из кэша значение ключа `key`."""
        value = await self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def invalidate(
        self,
        keys: list[str] | None = None,
        pattern: str | None = None
    ) -> None:
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

    async def invalidate_on_menu_create(self) -> None:
        """Инвалидация кэша при создании меню."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}'
            ]
        )

    async def invalidate_on_menu_update(self, menu_id: uuid.UUID) -> None:
        """Инвалидация кэша при обновлении меню."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}',
                f'{OBJ_PREFIX}:{menu_id}'
            ]
        )

    async def invalidate_on_menu_delete(self, menu_id: uuid.UUID) -> None:
        """Инвалидация кэша при удалении меню."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}',
            ],
            pattern=f'*{menu_id}*'
        )

    async def invalidate_on_submenu_create(self, menu_id: uuid.UUID) -> None:
        """Инвалидация кэша при создании субменю."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}'
            ]
        )

    async def invalidate_on_submenu_update(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID
    ) -> None:
        """Инвалидация кэша при обновлении субменю."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}'
            ]
        )

    async def invalidate_on_submenu_delete(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID
    ) -> None:
        """Инвалидация кэша при удалении субменю."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}',
            ],
            pattern=f'*{submenu_id}*'
        )

    async def invalidate_on_dish_create(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID
    ) -> None:
        """Инвалидация кэша при создании блюда."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{LIST_PREFIX}:{menu_id}:{submenu_id}',
                f'{OBJ_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}'
            ]
        )

    async def invalidate_on_dish_update(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID
    ) -> None:
        """Инвалидация кэша при обновлении блюда."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}:{submenu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}'
            ]
        )

    async def invalidate_on_dish_delete(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID
    ) -> None:
        """Инвалидация кэша при удалении блюда."""
        await self.invalidate(
            keys=[
                f'{ALL_NESTED_PREFIX}',
                f'{LIST_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{LIST_PREFIX}:{menu_id}:{submenu_id}',
                f'{OBJ_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}',
            ],
            pattern=f'*{dish_id}*'
        )


cache = RedisCache()
