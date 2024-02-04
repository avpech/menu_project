import uuid

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_types import MenuAnnotatedDict
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
    ) -> list[MenuAnnotatedDict]:
        """Получение всех объектов с аннотациями."""
        db_objs = await session.execute(
            select(Menu, func.count(distinct(Submenu.id)), func.count(Dish.id))
            .select_from(Menu)
            .join(Submenu, isouter=True)
            .join(Submenu.dishes, isouter=True)
            .group_by(Menu.id)
        )
        return [
            {
                'id': menu.id,
                'title': menu.title,
                'description': menu.description,
                'submenus_count': submenus_count,
                'dishes_count': dishes_count
            } for menu, submenus_count, dishes_count in db_objs
        ]

    async def get_annotated(
        self,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> MenuAnnotatedDict | None:
        """Получение объекта с аннотациями по id."""
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
        return {
            'id': menu.id,
            'title': menu.title,
            'description': menu.description,
            'submenus_count': submenus_count,
            'dishes_count': dishes_count
        }

    async def get_annotated_or_404(
        self,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> MenuAnnotatedDict:
        """
        Получение объекта с аннотациями по id.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_annotated(obj_id, session)
        return self._exists_or_404(obj, detail='menu not found')


menu_crud = CRUDMenu(Menu)
