import uuid
from typing import Sequence

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_types import (
    MenuAnnotatedDict,
    MenuCachedDict,
    MenuCachedNestedDiscountDict,
    MenuNestedDiscountDict,
)
from app.core.redis_cache import ALL_NESTED_PREFIX, LIST_PREFIX, OBJ_PREFIX, cache
from app.crud import menu_crud
from app.models import Menu
from app.schemas.menu import MenuCreate, MenuUpdate
from app.services.validators import check_menu_title_duplicate


class MenuService:
    """Взаимодействие с меню."""

    async def get_all_nested(
        self,
        session: AsyncSession
    ) -> Sequence[MenuNestedDiscountDict | MenuCachedNestedDiscountDict]:
        """Получить список меню с вложенными подменю и блюдами."""
        menu_list_cache: list[MenuCachedNestedDiscountDict] | None = await cache.get(f'{ALL_NESTED_PREFIX}')
        if menu_list_cache is not None:
            return menu_list_cache
        menu_list = await menu_crud.get_all_with_discount(session)
        await cache.set(f'{ALL_NESTED_PREFIX}', menu_list)
        return menu_list

    async def get_list(
        self,
        session: AsyncSession
    ) -> Sequence[MenuAnnotatedDict | MenuCachedDict]:
        """Получить список меню."""
        menu_list_cache: list[MenuCachedDict] | None = await cache.get(f'{LIST_PREFIX}')
        if menu_list_cache is not None:
            return menu_list_cache
        menu_list = await menu_crud.get_multi_annotated(session)
        await cache.set(f'{LIST_PREFIX}', menu_list)
        return menu_list

    async def create(
        self,
        menu: MenuCreate,
        session: AsyncSession,
        background_tasks: BackgroundTasks
    ) -> Menu:
        """Создать меню."""
        await check_menu_title_duplicate(menu.title, session)
        new_menu = await menu_crud.create(menu, session)
        background_tasks.add_task(cache.invalidate_on_menu_create)
        return new_menu

    async def get(
        self,
        menu_id: uuid.UUID,
        session: AsyncSession
    ) -> MenuAnnotatedDict | MenuCachedDict:
        """Получить меню."""
        menu_cache: MenuCachedDict | None = await cache.get(f'{OBJ_PREFIX}:{menu_id}')
        if menu_cache is not None:
            return menu_cache
        menu = await menu_crud.get_annotated_or_404(menu_id, session)
        await cache.set(f'{OBJ_PREFIX}:{menu_id}', menu)
        return menu

    async def update(
        self,
        menu_id: uuid.UUID,
        obj_in: MenuUpdate,
        session: AsyncSession,
        background_tasks: BackgroundTasks
    ) -> Menu:
        """Обновить меню."""
        menu = await menu_crud.get_or_404(menu_id, session)
        if obj_in.title is not None and obj_in.title != menu.title:
            await check_menu_title_duplicate(obj_in.title, session)
        updated_menu = await menu_crud.update(menu, obj_in, session)
        background_tasks.add_task(cache.invalidate_on_menu_update, menu_id)
        return updated_menu

    async def delete(
        self,
        menu_id: uuid.UUID,
        session: AsyncSession,
        background_tasks: BackgroundTasks
    ) -> Menu:
        """Удалить меню."""
        menu = await menu_crud.get_or_404(menu_id, session)
        deleted_menu = await menu_crud.remove(menu, session)
        background_tasks.add_task(cache.invalidate_on_menu_delete, menu_id)
        return deleted_menu


menu_service = MenuService()
