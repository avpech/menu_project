import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_types import DishCacheDict
from app.core.redis_cache import LIST_PREFIX, OBJ_PREFIX, cache
from app.crud import dish_crud
from app.models import Dish
from app.schemas.dish import DishCreate, DishUpdate
from app.services.validators import check_submenu_url_exists


class DishService:
    """Взаимодействие с блюдами."""

    async def get_list(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession
    ) -> Sequence[Dish | DishCacheDict]:
        """Получить список блюд."""
        dish_list_cache: list[DishCacheDict] | None = await cache.get(f'{LIST_PREFIX}:{menu_id}:{submenu_id}')
        if dish_list_cache is not None:
            return dish_list_cache
        dish_list = await dish_crud.get_multi_filtered(menu_id, submenu_id, session)
        await cache.set(f'{LIST_PREFIX}:{menu_id}:{submenu_id}', dish_list)
        return dish_list

    async def create(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish: DishCreate,
        session: AsyncSession
    ) -> Dish:
        """Создать блюдо."""
        await check_submenu_url_exists(menu_id, submenu_id, session)
        new_dish = await dish_crud.create(dish, session, submenu_id=submenu_id)
        await cache.invalidate(
            keys=[
                f'{LIST_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{LIST_PREFIX}:{menu_id}:{submenu_id}',
                f'{OBJ_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}'
            ]
        )
        return new_dish

    async def get(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        session: AsyncSession
    ) -> Dish | DishCacheDict:
        """Получить блюдо."""
        dish_cache: DishCacheDict | None = await cache.get(f'{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}')
        if dish_cache is not None:
            return dish_cache
        dish = await dish_crud.get_filtered_or_404(menu_id, submenu_id, dish_id, session)
        await cache.set(f'{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}', dish)
        return dish

    async def update(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        obj_in: DishUpdate,
        session: AsyncSession
    ) -> Dish:
        """Обновить блюдо."""
        dish = await dish_crud.get_filtered_or_404(menu_id, submenu_id, dish_id, session)
        updated_dish = await dish_crud.update(dish, obj_in, session)
        await cache.invalidate(
            keys=[
                f'{LIST_PREFIX}:{menu_id}:{submenu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}'
            ]
        )
        return updated_dish

    async def delete(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        session: AsyncSession
    ) -> Dish:
        """Удалить блюдо."""
        dish = await dish_crud.get_filtered_or_404(menu_id, submenu_id, dish_id, session)
        deleted_dish = await dish_crud.remove(dish, session)
        await cache.invalidate(
            keys=[
                f'{LIST_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{LIST_PREFIX}:{menu_id}:{submenu_id}',
                f'{OBJ_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}',
            ]
        )
        return deleted_dish


dish_service = DishService()
