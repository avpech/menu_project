import uuid
from http import HTTPStatus
from typing import Sequence

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    DELETE_TAG,
    GET_LIST_TAG,
    GET_TAG,
    MENU_ID_DESCR,
    PATCH_TAG,
    POST_TAG,
    SUBMENU_ID_DESCR,
)
from app.core.custom_types import SubmenuAnnotatedDict, SubmenuCachedDict
from app.core.db import get_async_session
from app.models import Submenu
from app.schemas.errors import SubmenuNotFoundError, URLDoesNotExistError
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
    response_model=list[SubmenuWithCountDB],
    responses={404: {'model': URLDoesNotExistError}},
    summary='Получение списка подменю',
    response_description='Успешное получение списка подменю',
    tags=[GET_LIST_TAG]
)
async def get_all_submenus(
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[SubmenuAnnotatedDict | SubmenuCachedDict]:
    """
    Получить список всех подменю.

    - **id**: Идентификатор подменю.
    - **title**: Название подменю.
    - **description**: Описание подменю.
    - **menu_id**: Идентификатор связанного меню.
    - **dishes_count**: Количество блюд в подменю.
    """
    return await submenu_service.get_list(menu_id, session)


@router.post(
    '/{menu_id}/submenus',
    response_model=SubmenuDB,
    status_code=HTTPStatus.CREATED,
    responses={404: {'model': URLDoesNotExistError}},
    summary='Создание нового подменю',
    response_description='Успешное создание нового подменю',
    tags=[POST_TAG]
)
async def create_submenu(
    submenu: SubmenuCreate,
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    session: AsyncSession = Depends(get_async_session)
) -> Submenu:
    """
    Создать подменю.

    - **id**: Идентификатор подменю.
    - **title**: Название подменю.
    - **description**: Описание подменю.
    - **menu_id**: Идентификатор связанного меню.
    """
    return await submenu_service.create(menu_id, submenu, session)


@router.get(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuWithCountDB,
    responses={404: {'model': SubmenuNotFoundError}},
    summary='Получение подменю',
    response_description='Успешное получение подменю',
    tags=[GET_TAG]
)
async def get_submenu(
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    submenu_id: uuid.UUID = Path(..., description=SUBMENU_ID_DESCR),
    session: AsyncSession = Depends(get_async_session)
) -> SubmenuAnnotatedDict | SubmenuCachedDict:
    """
    Получить подменю по id.

    - **id**: Идентификатор подменю.
    - **title**: Название подменю.
    - **description**: Описание подменю.
    - **menu_id**: Идентификатор связанного меню.
    - **dishes_count**: Количество блюд в подменю.
    """
    return await submenu_service.get(menu_id, submenu_id, session)


@router.patch(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuDB,
    responses={404: {'model': SubmenuNotFoundError}},
    summary='Обновление существующего подменю',
    response_description='Успешное обновление подменю',
    tags=[PATCH_TAG]
)
async def update_submenu(
    obj_in: SubmenuUpdate,
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    submenu_id: uuid.UUID = Path(..., description=SUBMENU_ID_DESCR),
    session: AsyncSession = Depends(get_async_session)
) -> Submenu:
    """
    Изменить подменю.

    - **id**: Идентификатор подменю.
    - **title**: Название подменю.
    - **description**: Описание подменю.
    - **menu_id**: Идентификатор связанного меню.
    """
    return await submenu_service.update(menu_id, submenu_id, obj_in, session)


@router.delete(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=SubmenuDB,
    responses={404: {'model': SubmenuNotFoundError}},
    summary='Удаление подменю',
    response_description='Успешное удаление подменю',
    tags=[DELETE_TAG]
)
async def delete_submenu(
    menu_id: uuid.UUID = Path(..., description=MENU_ID_DESCR),
    submenu_id: uuid.UUID = Path(..., description=SUBMENU_ID_DESCR),
    session: AsyncSession = Depends(get_async_session)
) -> Submenu:
    """
    Удалить подменю.

    - **id**: Идентификатор подменю.
    - **title**: Название подменю.
    - **description**: Описание подменю.
    - **menu_id**: Идентификатор связанного меню.
    """
    return await submenu_service.delete(menu_id, submenu_id, session)
