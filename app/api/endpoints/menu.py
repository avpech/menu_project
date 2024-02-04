import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.schemas.menu import MenuCreate, MenuDB, MenuUpdate, MenuWithCountDB
from app.services import menu_service

router = APIRouter()


@router.get('/', response_model=list[MenuWithCountDB])
async def get_all_menus(
    session: AsyncSession = Depends(get_async_session)
):
    """Получить список всех меню."""
    return await menu_service.get_list(session)


@router.post('/', response_model=MenuDB, status_code=HTTPStatus.CREATED)
async def create_menu(
    menu: MenuCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Создать меню.

    - **title**: Название меню.
    - **description**: Описание меню.
    """
    return await menu_service.create(menu, session)


@router.get('/{menu_id}', response_model=MenuWithCountDB)
async def get_menu(
    menu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Получить меню по id."""
    return await menu_service.get(menu_id, session)


@router.patch('/{menu_id}', response_model=MenuDB)
async def update_menu(
    menu_id: uuid.UUID,
    obj_in: MenuUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Изменить меню.

    - **title**: Название меню.
    - **description**: Описание меню.
    """
    return await menu_service.update(menu_id, obj_in, session)


@router.delete('/{menu_id}', response_model=MenuDB)
async def delete_menu(
    menu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Удалить меню."""
    return await menu_service.delete(menu_id, session)
