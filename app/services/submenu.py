import uuid
from typing import Sequence

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_types import SubmenuAnnotatedDict, SubmenuCachedDict
from app.core.redis_cache import LIST_PREFIX, OBJ_PREFIX, cache
from app.crud import submenu_crud
from app.models import Submenu
from app.schemas.submenu import SubmenuCreate, SubmenuUpdate
from app.services.validators import check_menu_url_exists, check_submenu_title_duplicate


class SubmenuService:
    """Взаимодействие с субменю."""

    async def get_list(
        self,
        menu_id: uuid.UUID,
        session: AsyncSession
    ) -> Sequence[SubmenuAnnotatedDict | SubmenuCachedDict]:
        """Получить список субменю."""
        submenu_list_cache: list[SubmenuCachedDict] | None = await cache.get(f'{LIST_PREFIX}:{menu_id}')
        if submenu_list_cache is not None:
            return submenu_list_cache
        submenu_list = await submenu_crud.get_multi_filtered_annotated(menu_id, session)
        await cache.set(f'{LIST_PREFIX}:{menu_id}', submenu_list)
        return submenu_list

    async def create(
        self,
        menu_id: uuid.UUID,
        submenu: SubmenuCreate,
        session: AsyncSession,
        background_tasks: BackgroundTasks
    ) -> Submenu:
        """Создать субменю."""
        await check_submenu_title_duplicate(submenu.title, session)
        await check_menu_url_exists(menu_id, session)
        new_submenu = await submenu_crud.create(submenu, session, menu_id=menu_id)
        background_tasks.add_task(cache.invalidate_on_submenu_create, menu_id)
        return new_submenu

    async def get(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession
    ) -> SubmenuAnnotatedDict | SubmenuCachedDict:
        """Получить субменю."""
        submenu_cache: SubmenuCachedDict | None = await cache.get(f'{OBJ_PREFIX}:{menu_id}:{submenu_id}')
        if submenu_cache is not None:
            return submenu_cache
        submenu = await submenu_crud.get_filtered_annotated_or_404(menu_id, submenu_id, session)
        await cache.set(f'{OBJ_PREFIX}:{menu_id}:{submenu_id}', submenu)
        return submenu

    async def update(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        obj_in: SubmenuUpdate,
        session: AsyncSession,
        background_tasks: BackgroundTasks
    ) -> Submenu:
        """Обновить субменю."""
        submenu = await submenu_crud.get_filtered_or_404(menu_id, submenu_id, session)
        if obj_in.title is not None and obj_in.title != submenu.title:
            await check_submenu_title_duplicate(obj_in.title, session)
        updated_submenu = await submenu_crud.update(submenu, obj_in, session)
        background_tasks.add_task(cache.invalidate_on_submenu_update, menu_id, submenu_id)
        return updated_submenu

    async def delete(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession,
        background_tasks: BackgroundTasks
    ) -> Submenu:
        """Удалить субменю."""
        submenu = await submenu_crud.get_filtered_or_404(menu_id, submenu_id, session)
        deleted_submenu = await submenu_crud.remove(submenu, session)
        background_tasks.add_task(cache.invalidate_on_submenu_delete, menu_id, submenu_id)
        return deleted_submenu


submenu_service = SubmenuService()
