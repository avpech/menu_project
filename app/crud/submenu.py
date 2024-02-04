import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_types import SubmenuAnnotatedDict
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
    ) -> list[SubmenuAnnotatedDict]:
        """Получение списка отфильтрованных по `menu_id` объектов с аннотациями."""
        db_objs = await session.execute(
            select(Submenu, func.count(Dish.id))
            .join(Dish, isouter=True)
            .where(Submenu.menu_id == menu_id)
            .group_by(Submenu.id)
        )
        return [
            {
                'id': submenu.id,
                'title': submenu.title,
                'description': submenu.description,
                'menu_id': submenu.menu_id,
                'dishes_count': dishes_count
            } for submenu, dishes_count in db_objs
        ]

    async def get_filtered_annotated(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> SubmenuAnnotatedDict | None:
        """
        Получение объекта с аннотациями по id,
        если он связан с соответствующим меню.
        """
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
        return {
            'id': submenu.id,
            'title': submenu.title,
            'description': submenu.description,
            'menu_id': submenu.menu_id,
            'dishes_count': dishes_count
        }

    async def get_filtered_annotated_or_404(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> SubmenuAnnotatedDict:
        """
        Получение объекта с аннотациями по id,
        если он связан с соответствующим меню.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_filtered_annotated(menu_id, obj_id, session)
        return self._exists_or_404(obj, detail='submenu not found')

    async def get_filtered(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Submenu | None:
        """Получение объекта по id, если он связан с соответствующим меню."""
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
        Получение объекта по id, если он связан с соответствующим меню.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_filtered(menu_id, obj_id, session)
        return self._exists_or_404(obj, detail='submenu not found')


submenu_crud = CRUDSubmenu(Submenu)
