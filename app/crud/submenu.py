import uuid
from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Dish, Submenu
from app.schemas.submenu import SubmenuCreate, SubmenuUpdate


class CRUDSubmenu(
    CRUDBase[Submenu, SubmenuCreate, SubmenuUpdate]
):
    """Класс CRUD-операций для модели Submenu."""

    async def get_multi(
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

    async def create(
        self,
        menu_id: uuid.UUID,
        obj_in: SubmenuCreate,
        session: AsyncSession
    ) -> Submenu:
        """Создание объекта."""
        obj_in_data = obj_in.model_dump()
        db_obj = Submenu(**obj_in_data, menu_id=menu_id)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Optional[Submenu]:
        """Получение объекта по UUID."""
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

    async def get_or_404(
        self,
        menu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Optional[Submenu]:
        obj = await self.get(menu_id, obj_id, session)
        if obj is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='submenu not found'
            )
        return obj


submenu_crud = CRUDSubmenu(Submenu)
