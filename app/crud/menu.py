import uuid
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Dish, Menu, Submenu
from app.schemas.menu import MenuCreate, MenuUpdate


class CRUDMenu(
    CRUDBase[Menu, MenuCreate, MenuUpdate]
):
    """Класс CRUD-операций для модели Menu."""

    async def get_multi_annotated(
        self,
        session: AsyncSession
    ) -> list[Menu]:
        """Получение всех объектов."""
        db_objs = await session.execute(
            select(Menu, func.count(distinct(Submenu.id)), func.count(Dish.id))
            .select_from(Menu)
            .join(Submenu, isouter=True)
            .join(Submenu.dishes, isouter=True)
            .group_by(Menu.id)
        )
        menus = []
        for db_obj in db_objs:
            menu, submenus_count, dishes_count = db_obj
            menu.submenus_count = submenus_count
            menu.dishes_count = dishes_count
            menus.append(menu)
        return menus

    async def get_annotated(
        self,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Menu | None:
        """Получение объекта по id."""
        db_obj = await session.execute(
            select(Menu, func.count(distinct(Submenu.id)), func.count(Dish.id))
            .select_from(Menu)
            .join(Submenu, isouter=True)
            .join(Submenu.dishes, isouter=True)
            .where(Menu.id == obj_id)
            .group_by(Menu.id)
        )
        db_obj = db_obj.first()
        if db_obj is None:
            return None
        menu, submenus_count, dishes_count = db_obj
        menu.submenus_count = submenus_count
        menu.dishes_count = dishes_count
        return menu

    async def get_annotated_or_404(
        self,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Menu:
        """
        Получение объекта по id.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_annotated(obj_id, session)
        if obj is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='menu not found'
            )
        return obj


menu_crud = CRUDMenu(Menu)
