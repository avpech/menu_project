import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.schemas.dish import DishCreate, DishDB, DishUpdate
from app.services import dish_service

router = APIRouter()


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=list[DishDB]
)
async def get_all_dishes(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Получить список всех блюд."""
    return await dish_service.get_list(menu_id, submenu_id, session)


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=DishDB,
    status_code=HTTPStatus.CREATED
)
async def create_dish(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish: DishCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Добавить блюдо.

    - **title**: Название блюда.
    - **description**: Описание блюда.
    - **price**: Цена блюда.
    """
    return await dish_service.create(menu_id, submenu_id, dish, session)


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=DishDB
)
async def get_dish(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Получить блюдо по id."""
    return await dish_service.get(menu_id, submenu_id, dish_id, session)


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=DishDB
)
async def update_dish(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish_id: uuid.UUID,
    obj_in: DishUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Изменить блюдо.

    - **title**: Название блюда.
    - **description**: Описание блюда.
    - **price**: Цена блюда.
    """
    return await dish_service.update(menu_id, submenu_id, dish_id, obj_in, session)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=DishDB
)
async def delete_dish(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """Удалить блюдо."""
    return await dish_service.delete(menu_id, submenu_id, dish_id, session)
