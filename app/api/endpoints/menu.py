import uuid
from http import HTTPStatus
from typing import Sequence

from fastapi import APIRouter, BackgroundTasks, Depends, Path

from app.core.constants import (
    DELETE_TAG,
    GET_LIST_TAG,
    GET_TAG,
    MENU_ID_DESCR,
    PATCH_TAG,
    POST_TAG,
)
from app.core.custom_types import (
    MenuAnnotatedDict,
    MenuCachedDict,
    MenuCachedNestedDiscountDict,
    MenuNestedDiscountDict,
)
from app.models import Menu
from app.schemas.errors import MenuNotFoundError
from app.schemas.menu import (
    MenuCreate,
    MenuDB,
    MenuNestedSubmenusDB,
    MenuUpdate,
    MenuWithCountDB,
)
from app.services.menu import MenuService

router = APIRouter()


@router.get(
    '/',
    response_model=list[MenuWithCountDB],
    summary='Получение списка меню',
    response_description='Успешное получение списка меню',
    tags=[GET_LIST_TAG]
)
async def get_all_menus(
    menu_service: MenuService = Depends()
) -> Sequence[MenuAnnotatedDict | MenuCachedDict]:
    """
    Получить список всех меню.

    - **id**: Идентификатор меню.
    - **title**: Название меню.
    - **description**: Описание меню.
    - **submenus_count**: Количество подменю в меню.
    - **dishes_count**: Количество блюд в меню.
    """
    return await menu_service.get_list()


@router.get(
    '/all',
    response_model=list[MenuNestedSubmenusDB],
    summary='Получение списка меню с вложенными подменю и блюдами',
    response_description='Успешное получение списка меню',
    tags=[GET_LIST_TAG]
)
async def get_all_nested(
    menu_service: MenuService = Depends()
) -> Sequence[MenuNestedDiscountDict | MenuCachedNestedDiscountDict]:
    """Получить список всех меню с вложенными подменю и блюдами."""
    return await menu_service.get_all_nested()


@router.post(
    '/',
    response_model=MenuDB,
    status_code=HTTPStatus.CREATED,
    summary='Создание нового меню',
    response_description='Успешное создание нового меню',
    tags=[POST_TAG]
)
async def create_menu(
    menu: MenuCreate,
    menu_service: MenuService = Depends(),
    *,
    background_tasks: BackgroundTasks,
) -> Menu:
    """
    Создать меню.

    - **id**: Идентификатор меню.
    - **title**: Название меню.
    - **description**: Описание меню.
    """
    return await menu_service.create(menu, background_tasks)


@router.get(
    '/{menu_id}',
    response_model=MenuWithCountDB,
    responses={404: {'model': MenuNotFoundError}},
    summary='Получение меню',
    response_description='Успешное получение меню',
    tags=[GET_TAG]
)
async def get_menu(
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    menu_service: MenuService = Depends()
) -> MenuAnnotatedDict | MenuCachedDict:
    """
    Получить меню по id.

    - **id**: Идентификатор меню.
    - **title**: Название меню.
    - **description**: Описание меню.
    - **submenus_count**: Количество подменю в меню.
    - **dishes_count**: Количество блюд в меню.
    """
    return await menu_service.get(menu_id)


@router.patch(
    '/{menu_id}',
    response_model=MenuDB,
    responses={404: {'model': MenuNotFoundError}},
    summary='Обновление существующего меню',
    response_description='Успешное обновление меню',
    tags=[PATCH_TAG]
)
async def update_menu(
    obj_in: MenuUpdate,
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    menu_service: MenuService = Depends(),
    *,
    background_tasks: BackgroundTasks
) -> Menu:
    """
    Изменить меню.

    - **id**: Идентификатор меню.
    - **title**: Название меню.
    - **description**: Описание меню.
    """
    return await menu_service.update(menu_id, obj_in, background_tasks)


@router.delete(
    '/{menu_id}',
    response_model=MenuDB,
    responses={404: {'model': MenuNotFoundError}},
    summary='Удаление меню',
    response_description='Успешное удаление меню',
    tags=[DELETE_TAG]
)
async def delete_menu(
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    menu_service: MenuService = Depends(),
    *,
    background_tasks: BackgroundTasks
) -> Menu:
    """
    Удалить меню.

    - **id**: Идентификатор меню.
    - **title**: Название меню.
    - **description**: Описание меню.
    """
    return await menu_service.delete(menu_id, background_tasks)
