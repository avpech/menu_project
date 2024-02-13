import uuid
from typing import Sequence

from fastapi import BackgroundTasks, Depends

from app.core.custom_types import (
    MenuAnnotatedDict,
    MenuCachedDict,
    MenuCachedNestedDiscountDict,
    MenuNestedDiscountDict,
)
from app.core.redis_cache import ALL_NESTED_PREFIX, LIST_PREFIX, OBJ_PREFIX, cache
from app.crud.menu import CRUDMenu
from app.models import Menu
from app.schemas.menu import MenuCreate, MenuUpdate
from app.services.validators import check_menu_title_duplicate


class MenuService:
    """Взаимодействие с меню."""

    def __init__(self, crud: CRUDMenu = Depends()) -> None:
        self.crud = crud

    async def get_all_nested(
        self
    ) -> Sequence[MenuNestedDiscountDict | MenuCachedNestedDiscountDict]:
        """Получить список меню с вложенными подменю и блюдами."""
        menu_list_cache: list[MenuCachedNestedDiscountDict] | None = await cache.get(f'{ALL_NESTED_PREFIX}')
        if menu_list_cache is not None:
            return menu_list_cache
        menu_list = await self.crud.get_all_with_discount()
        await cache.set(f'{ALL_NESTED_PREFIX}', menu_list)
        return menu_list

    async def get_list(self) -> Sequence[MenuAnnotatedDict | MenuCachedDict]:
        """Получить список меню."""
        menu_list_cache: list[MenuCachedDict] | None = await cache.get(f'{LIST_PREFIX}')
        if menu_list_cache is not None:
            return menu_list_cache
        menu_list = await self.crud.get_multi_annotated()
        await cache.set(f'{LIST_PREFIX}', menu_list)
        return menu_list

    async def create(
        self,
        menu: MenuCreate,
        background_tasks: BackgroundTasks
    ) -> Menu:
        """Создать меню."""
        await check_menu_title_duplicate(menu.title, self.crud.session)
        new_menu = await self.crud.create(menu)
        background_tasks.add_task(cache.invalidate_on_menu_create)
        return new_menu

    async def get(
        self,
        menu_id: uuid.UUID
    ) -> MenuAnnotatedDict | MenuCachedDict:
        """Получить меню."""
        menu_cache: MenuCachedDict | None = await cache.get(f'{OBJ_PREFIX}:{menu_id}')
        if menu_cache is not None:
            return menu_cache
        menu = await self.crud.get_annotated_or_404(menu_id)
        await cache.set(f'{OBJ_PREFIX}:{menu_id}', menu)
        return menu

    async def update(
        self,
        menu_id: uuid.UUID,
        obj_in: MenuUpdate,
        background_tasks: BackgroundTasks
    ) -> Menu:
        """Обновить меню."""
        menu = await self.crud.get_or_404(menu_id)
        if obj_in.title is not None and obj_in.title != menu.title:
            await check_menu_title_duplicate(obj_in.title, self.crud.session)
        updated_menu = await self.crud.update(menu, obj_in)
        background_tasks.add_task(cache.invalidate_on_menu_update, menu_id)
        return updated_menu

    async def delete(
        self,
        menu_id: uuid.UUID,
        background_tasks: BackgroundTasks
    ) -> Menu:
        """Удалить меню."""
        menu = await self.crud.get_or_404(menu_id)
        deleted_menu = await self.crud.remove(menu)
        background_tasks.add_task(cache.invalidate_on_menu_delete, menu_id)
        return deleted_menu
