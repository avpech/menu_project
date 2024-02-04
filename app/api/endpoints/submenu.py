import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.schemas.submenu import (
    SubmenuCreate,
    SubmenuDB,
    SubmenuUpdate,
    SubmenuWithCountDB,
)
from app.services import submenu_service

router = APIRouter()


@router.get(
    '/{menu_id}/submenus',
    response_model=list[SubmenuWithCountDB]
)
async def get_all_submenus(
    menu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Получить список всех подменю."""
    return await submenu_service.get_list(menu_id, session)


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
    """
    Создать подменю.

    - **title**: Название подменю.
    - **description**: Описание подменю.
    """
    return await submenu_service.create(menu_id, submenu, session)


@router.get(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuWithCountDB
)
async def get_submenu(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Получить подменю по id."""
    return await submenu_service.get(menu_id, submenu_id, session)


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
    """
    Изменить подменю.

    - **title**: Название подменю.
    - **description**: Описание подменю.
    """
    return await submenu_service.update(menu_id, submenu_id, obj_in, session)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuDB
)
async def delete_submenu(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Удалить подменю."""
    return await submenu_service.delete(menu_id, submenu_id, session)
