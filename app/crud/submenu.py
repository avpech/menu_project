import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Dish, Submenu
from app.schemas.submenu import SubmenuCreate, SubmenuUpdate


class CRUDSubmenu(
    CRUDBase[Submenu, SubmenuCreate, SubmenuUpdate]
):
    """Класс CRUD-операций для модели Submenu."""

    async def get_multi_filtered_annotated(
        self,
        menu_id: uuid.UUID,
        session: AsyncSession
    ) -> list[Submenu]:
        """Получение всех объектов."""
        db_objs = await session.execute(
            select(Submenu, func.count(Dish.id))
            .join(Dish, isouter=True)
            .where(Submenu.menu_id == menu_id)
            .group_by(Submenu.id)
        )
        submenus = []
        for db_obj in db_objs:
            submenu, dishes_count = db_obj
            submenu.dishes_count = dishes_count
            submenus.append(submenu)
        return submenus

    async def get_filtered_annotated(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Submenu | None:
        """Получение объекта по id."""
        db_obj = await session.execute(
            select(Submenu, func.count(Dish.id))
            .join(Dish, isouter=True)
            .where(Submenu.id == obj_id, Submenu.menu_id == menu_id)
            .group_by(Submenu.id)
        )
        db_obj = db_obj.first()
        if db_obj is None:
            return None
        submenu, dishes_count = db_obj
        submenu.dishes_count = dishes_count
        return submenu

    async def get_filtered_annotated_or_404(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Submenu:
        """
        Получение объекта по id.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_filtered_annotated(menu_id, obj_id, session)
        obj = self._exists_or_404(obj, detail='submenu not found')
        return obj

    async def get_filtered(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Submenu | None:
        """Получение объекта по id."""
        submenu = await session.execute(
            select(Submenu)
            .where(Submenu.id == obj_id, Submenu.menu_id == menu_id)
        )
        return submenu.scalars().first()

    async def get_filtered_or_404(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Submenu:
        """
        Получение объекта по id.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_filtered(menu_id, obj_id, session)
        obj = self._exists_or_404(obj, detail='submenu not found')
        return obj


submenu_crud = CRUDSubmenu(Submenu)
