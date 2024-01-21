import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_menu_title_duplicate
from app.core.db import get_async_session
from app.crud import menu_crud
from app.schemas.menu import MenuCreate, MenuDB, MenuUpdate, MenuWithCountDB

router = APIRouter()


@router.get('/', response_model=list[MenuWithCountDB])
async def get_all_menu(
    session: AsyncSession = Depends(get_async_session)
):
    """Получить список всех меню."""
    return await menu_crud.get_multi(session)


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
    await check_menu_title_duplicate(menu.title, session)
    return await menu_crud.create(menu, session)


@router.get('/{menu_id}', response_model=MenuWithCountDB)
async def get_menu(
    menu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Получить меню по id."""
    return await menu_crud.get_or_404(menu_id, session)


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
    menu = await menu_crud.get_or_404(menu_id, session)
    if obj_in.title is not None and obj_in.title != menu.title:
        await check_menu_title_duplicate(obj_in.title, session)
    return await menu_crud.update(menu, obj_in, session)


@router.delete('/{menu_id}', response_model=MenuDB)
async def delete_menu(
    menu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Удалить меню."""
    menu = await menu_crud.get_or_404(menu_id, session)
    return await menu_crud.remove(menu, session)
