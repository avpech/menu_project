import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_submenu_url_exists
from app.core.db import get_async_session
from app.crud import dish_crud
from app.schemas.dish import DishCreate, DishDB, DishUpdate

router = APIRouter()


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
    await check_submenu_url_exists(menu_id, submenu_id, session)
    return await dish_crud.create(submenu_id, dish, session)


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=list[DishDB]
)
async def get_all_dishes(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    return await dish_crud.get_multi(menu_id, submenu_id, session)


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
    return await dish_crud.get_or_404(menu_id, submenu_id, dish_id, session)


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
    dish = await dish_crud.get_or_404(menu_id, submenu_id, dish_id, session)
    return await dish_crud.update(dish, obj_in, session)


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
    dish = await dish_crud.get_or_404(menu_id, submenu_id, dish_id, session)
    return await dish_crud.remove(dish, session)
