import uuid
from http import HTTPStatus
from typing import Sequence

from fastapi import APIRouter, BackgroundTasks, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    DELETE_TAG,
    DISH_ID_DESCR,
    GET_LIST_TAG,
    GET_TAG,
    MENU_ID_DESCR,
    PATCH_TAG,
    POST_TAG,
    SUBMENU_ID_DESCR,
)
from app.core.custom_types import DishCachedDiscountDict, DishDiscountDict
from app.core.db import get_async_session
from app.models import Dish
from app.schemas.dish import DishCreate, DishDB, DishDiscountDB, DishUpdate
from app.schemas.errors import DishNotFoundError, URLDoesNotExistError
from app.services import dish_service

router = APIRouter()


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=list[DishDiscountDB],
    responses={404: {'model': URLDoesNotExistError}},
    summary='Получение списка блюд',
    response_description='Успешное получение списка блюд',
    tags=[GET_LIST_TAG]
)
async def get_all_dishes(
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    submenu_id: uuid.UUID = Path(..., description=SUBMENU_ID_DESCR),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[DishDiscountDict | DishCachedDiscountDict]:
    """
    Получить список всех блюд.

    - **id**: Идентификатор блюда.
    - **title**: Название блюда.
    - **description**: Описание блюда.
    - **price**: Цена блюда с учетом скидки.
    - **discount**: Скидка на блюдо.
    - **submenu_id**: Идентификатор связанного подменю.
    """
    return await dish_service.get_list(menu_id, submenu_id, session)


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=DishDB,
    status_code=HTTPStatus.CREATED,
    responses={404: {'model': URLDoesNotExistError}},
    summary='Создание нового блюда',
    response_description='Успешное создание нового блюда',
    tags=[POST_TAG]
)
async def create_dish(
    dish: DishCreate,
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    submenu_id: uuid.UUID = Path(..., description=SUBMENU_ID_DESCR),
    session: AsyncSession = Depends(get_async_session),
    *,
    background_tasks: BackgroundTasks
) -> Dish:
    """
    Добавить блюдо.

    - **id**: Идентификатор блюда.
    - **title**: Название блюда.
    - **description**: Описание блюда.
    - **price**: Цена блюда.
    - **submenu_id**: Идентификатор связанного подменю.
    """
    return await dish_service.create(menu_id, submenu_id, dish, session, background_tasks)


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=DishDiscountDB,
    responses={404: {'model': DishNotFoundError}},
    summary='Получение блюда',
    response_description='Успешное получение блюда',
    tags=[GET_TAG]
)
async def get_dish(
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    submenu_id: uuid.UUID = Path(..., description=SUBMENU_ID_DESCR),
    dish_id: uuid.UUID = Path(..., description=DISH_ID_DESCR),
    session: AsyncSession = Depends(get_async_session)
) -> DishDiscountDict | DishCachedDiscountDict:
    """
    Получить блюдо по id.

    - **id**: Идентификатор блюда.
    - **title**: Название блюда.
    - **description**: Описание блюда.
    - **price**: Цена блюда с учетом скидки.
    - **discount**: Скидка на блюдо.
    - **submenu_id**: Идентификатор связанного подменю.
    """
    return await dish_service.get(menu_id, submenu_id, dish_id, session)


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=DishDB,
    responses={404: {'model': DishNotFoundError}},
    summary='Обновление существующего блюда',
    response_description='Успешное обновление блюда',
    tags=[PATCH_TAG]
)
async def update_dish(
    obj_in: DishUpdate,
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    submenu_id: uuid.UUID = Path(..., description=SUBMENU_ID_DESCR),
    dish_id: uuid.UUID = Path(..., description=DISH_ID_DESCR),
    session: AsyncSession = Depends(get_async_session),
    *,
    background_tasks: BackgroundTasks
) -> Dish:
    """
    Изменить блюдо.

    - **id**: Идентификатор блюда.
    - **title**: Название блюда.
    - **description**: Описание блюда.
    - **price**: Цена блюда.
    - **submenu_id**: Идентификатор связанного подменю.
    """
    return await dish_service.update(menu_id, submenu_id, dish_id, obj_in, session, background_tasks)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=DishDB,
    responses={404: {'model': DishNotFoundError}},
    summary='Удаление блюда',
    response_description='Успешное удаление блюда',
    tags=[DELETE_TAG]
)
async def delete_dish(
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    submenu_id: uuid.UUID = Path(..., description=SUBMENU_ID_DESCR),
    dish_id: uuid.UUID = Path(..., description=DISH_ID_DESCR),
    session: AsyncSession = Depends(get_async_session),
    *,
    background_tasks: BackgroundTasks
) -> Dish:
    """
    Удалить блюдо.

    - **id**: Идентификатор блюда.
    - **title**: Название блюда.
    - **description**: Описание блюда.
    - **price**: Цена блюда.
    - **submenu_id**: Идентификатор связанного подменю.
    """
    return await dish_service.delete(menu_id, submenu_id, dish_id, session, background_tasks)
