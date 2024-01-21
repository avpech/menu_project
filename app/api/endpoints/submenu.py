import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_menu_url_exists
from app.core.db import get_async_session
from app.crud import submenu_crud
from app.schemas.submenu import (SubmenuCreate, SubmenuDB, SubmenuUpdate,
                                 SubmenuWithCountDB)

router = APIRouter()


@router.post(
    '/{menu_id}/submenus',
    response_model=SubmenuDB,
    status_code=HTTPStatus.CREATED
)
async def create_submenu(
    menu_id: uuid.UUID,
    submenu: SubmenuCreate,
    session: AsyncSession = Depends(get_async_session)
):
    await check_menu_url_exists(menu_id, session)
    return await submenu_crud.create(menu_id, submenu, session)


@router.get(
    '/{menu_id}/submenus',
    response_model=list[SubmenuWithCountDB]
)
async def get_all_submenu(
    menu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    return await submenu_crud.get_multi(menu_id, session)


@router.get(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuWithCountDB
)
async def get_submenu(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    return await submenu_crud.get_or_404(menu_id, submenu_id, session)


@router.patch(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuDB
)
async def update_submenu(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    obj_in: SubmenuUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    submenu = await submenu_crud.get_or_404(menu_id, submenu_id, session)
    return await submenu_crud.update(submenu, obj_in, session)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuDB
)
async def delete_submenu(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    submenu = await submenu_crud.get_or_404(menu_id, submenu_id, session)
    return await submenu_crud.remove(submenu, session)
