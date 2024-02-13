import uuid
from typing import Sequence

from fastapi import BackgroundTasks, Depends

from app.core.custom_types import DishCachedDiscountDict, DishDiscountDict
from app.core.redis_cache import LIST_PREFIX, OBJ_PREFIX, cache
from app.crud.dish import CRUDDish
from app.models import Dish
from app.schemas.dish import DishCreate, DishUpdate
from app.services.validators import check_dish_title_duplicate, check_submenu_url_exists


class DishService:
    """Взаимодействие с блюдами."""

    def __init__(self, crud: CRUDDish = Depends()) -> None:
        self.crud = crud

    async def get_list(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
    ) -> Sequence[DishDiscountDict | DishCachedDiscountDict]:
        """Получить список блюд."""
        dish_list_cache: list[DishCachedDiscountDict] | None = await cache.get(f'{LIST_PREFIX}:{menu_id}:{submenu_id}')
        if dish_list_cache is not None:
            return dish_list_cache
        dish_list = await self.crud.get_multi_filtered(menu_id, submenu_id)
        await cache.set(f'{LIST_PREFIX}:{menu_id}:{submenu_id}', dish_list)
        return dish_list

    async def create(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish: DishCreate,
        background_tasks: BackgroundTasks
    ) -> Dish:
        """Создать блюдо."""
        await check_dish_title_duplicate(dish.title, self.crud.session)
        await check_submenu_url_exists(menu_id, submenu_id, self.crud.session)
        new_dish = await self.crud.create(dish, submenu_id=submenu_id)
        background_tasks.add_task(cache.invalidate_on_dish_create, menu_id, submenu_id)
        return new_dish

    async def get(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID
    ) -> DishDiscountDict | DishCachedDiscountDict:
        """Получить блюдо."""
        dish_cache: DishCachedDiscountDict | None = await cache.get(f'{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}')
        if dish_cache is not None:
            return dish_cache
        dish = await self.crud.get_filtered_discounted_or_404(menu_id, submenu_id, dish_id)
        await cache.set(f'{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}', dish)
        return dish

    async def update(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        obj_in: DishUpdate,
        background_tasks: BackgroundTasks
    ) -> Dish:
        """Обновить блюдо."""
        dish = await self.crud.get_filtered_or_404(menu_id, submenu_id, dish_id)
        if obj_in.title is not None and obj_in.title != dish.title:
            await check_dish_title_duplicate(obj_in.title, self.crud.session)
        updated_dish = await self.crud.update(dish, obj_in)
        background_tasks.add_task(cache.invalidate_on_dish_update, menu_id, submenu_id, dish_id)
        return updated_dish

    async def delete(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        background_tasks: BackgroundTasks
    ) -> Dish:
        """Удалить блюдо."""
        dish = await self.crud.get_filtered_or_404(menu_id, submenu_id, dish_id)
        deleted_dish = await self.crud.remove(dish)
        background_tasks.add_task(cache.invalidate_on_dish_delete, menu_id, submenu_id, dish_id)
        return deleted_dish
