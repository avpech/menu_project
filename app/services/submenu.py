import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_cache import LIST_PREFIX, OBJ_PREFIX, cache
from app.crud import submenu_crud
from app.schemas.submenu import SubmenuCreate, SubmenuUpdate
from app.services.validators import check_menu_url_exists


class SubmenuService:

    async def get_list(
        self,
        menu_id: uuid.UUID,
        session: AsyncSession
    ):
        submenu_list_cache = await cache.get(f'{LIST_PREFIX}:{menu_id}')
        if submenu_list_cache is not None:
            return submenu_list_cache
        submenu_list = await submenu_crud.get_multi_filtered_annotated(menu_id, session)
        await cache.set(f'{LIST_PREFIX}:{menu_id}', submenu_list)
        return submenu_list

    async def create(
        self,
        menu_id: uuid.UUID,
        submenu: SubmenuCreate,
        session: AsyncSession
    ):
        await check_menu_url_exists(menu_id, session)
        new_submenu = await submenu_crud.create(submenu, session, menu_id=menu_id)
        await cache.invalidate(
            keys=[
                f'{LIST_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}'
            ]
        )
        return new_submenu

    async def get(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession
    ):
        submenu_cache = await cache.get(f'{OBJ_PREFIX}:{menu_id}:{submenu_id}')
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
        session: AsyncSession
    ):
        submenu = await submenu_crud.get_filtered_annotated_or_404(menu_id, submenu_id, session)
        updated_submenu = await submenu_crud.update(submenu, obj_in, session)
        await cache.invalidate(
            keys=[
                f'{LIST_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}:{submenu_id}'
            ]
        )
        return updated_submenu

    async def delete(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession
    ):
        submenu = await submenu_crud.get_filtered_annotated_or_404(menu_id, submenu_id, session)
        deleted_submenu = await submenu_crud.remove(submenu, session)
        await cache.invalidate(
            keys=[
                f'{LIST_PREFIX}',
                f'{LIST_PREFIX}:{menu_id}',
                f'{OBJ_PREFIX}:{menu_id}',
            ],
            pattern=f'*{submenu_id}*'
        )
        return deleted_submenu


submenu_service = SubmenuService()
