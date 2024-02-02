import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_cache import LIST_PREFIX, OBJ_PREFIX, cache
from app.crud import dish_crud
from app.schemas.dish import DishCreate, DishUpdate
from app.services.validators import check_submenu_url_exists


class DishService:

    async def get_list(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession
    ):
        """Получить список всех блюд."""
        dish_list_cache = await cache.get(f"{LIST_PREFIX}:{menu_id}:{submenu_id}")
        if dish_list_cache is not None:
            return dish_list_cache
        dish_list = await dish_crud.get_multi(menu_id, submenu_id, session)
        await cache.set(f"{LIST_PREFIX}:{menu_id}:{submenu_id}", dish_list)
        return dish_list

    async def create(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish: DishCreate,
        session: AsyncSession
    ):
        await check_submenu_url_exists(menu_id, submenu_id, session)
        new_dish = await dish_crud.create(submenu_id, dish, session)
        await cache.invalidate(
            keys=[
                f"{LIST_PREFIX}",
                f"{LIST_PREFIX}:{menu_id}",
                f"{LIST_PREFIX}:{menu_id}:{submenu_id}",
                f"{OBJ_PREFIX}:{menu_id}",
                f"{OBJ_PREFIX}:{menu_id}:{submenu_id}"
            ]
        )
        return new_dish

    async def get(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        session: AsyncSession
    ):
        dish_cache = await cache.get(f"{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}")
        if dish_cache is not None:
            return dish_cache
        dish = await dish_crud.get_or_404(menu_id, submenu_id, dish_id, session)
        await cache.set(f"{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}", dish)
        return dish

    async def update(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        obj_in: DishUpdate,
        session: AsyncSession
    ):
        dish = await dish_crud.get_or_404(menu_id, submenu_id, dish_id, session)
        updated_dish = await dish_crud.update(dish, obj_in, session)
        await cache.invalidate(
            keys=[
                f"{LIST_PREFIX}:{menu_id}:{submenu_id}",
                f"{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}"
            ]
        )
        return updated_dish

    async def delete(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        session: AsyncSession
    ):
        dish = await dish_crud.get_or_404(menu_id, submenu_id, dish_id, session)
        deleted_dish = await dish_crud.remove(dish, session)
        await cache.invalidate(
            keys=[
                f"{LIST_PREFIX}",
                f"{LIST_PREFIX}:{menu_id}",
                f"{LIST_PREFIX}:{menu_id}:{submenu_id}",
                f"{OBJ_PREFIX}:{menu_id}",
                f"{OBJ_PREFIX}:{menu_id}:{submenu_id}",
                f"{OBJ_PREFIX}:{menu_id}:{submenu_id}:{dish_id}",
            ]
        )
        return deleted_dish


dish_service = DishService()
