import uuid
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Menu, Submenu


class ErrorMessages:
    TITLE_DUPLICATE = 'Меню с таким названием уже существует'
    URL_NOT_FOUND = 'url not found'


async def check_menu_title_duplicate(
    menu_title: str,
    session: AsyncSession,
) -> None:
    """Проверка на отсутствие меню с переданным названием в базе данных."""
    exists_criteria = (
        select(Menu).where(Menu.title == menu_title)
    ).exists()
    menu_title_exists = await session.execute(
        select(True).where(exists_criteria)
    )
    if menu_title_exists.scalar():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorMessages.TITLE_DUPLICATE,
        )


async def check_menu_url_exists(
        menu_id: uuid.UUID,
        session: AsyncSession
) -> None:
    """Проверка наличия меню по url с указанным menu_id."""
    exists_criteria = (
        select(Menu).where(Menu.id == menu_id)
    ).exists()
    menu_url_exists = await session.execute(
        select(True).where(exists_criteria)
    )
    if menu_url_exists.scalar() is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.URL_NOT_FOUND,
        )


async def check_submenu_url_exists(
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession
) -> None:
    """Проверка наличия подменю по url с указанными menu_id и submenu_id."""
    menu_exists_criteria = (
        select(Menu).where(Menu.id == menu_id)
    ).exists()
    submenu_exists_criteria = (
        select(Submenu).where(Submenu.id == submenu_id)
    ).exists()
    submenu_url_exists = await session.execute(
        select(True).where(menu_exists_criteria, submenu_exists_criteria)
    )
    if submenu_url_exists.scalar() is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.URL_NOT_FOUND,
        )
