import uuid
from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Dish, Submenu
from app.schemas.dish import DishCreate, DishUpdate


class CRUDDish(
    CRUDBase[Dish, DishCreate, DishUpdate]
):
    """Класс CRUD-операций для модели Dish."""

    async def get_multi(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession
    ) -> list[Dish]:
        """Получение всех объектов."""
        db_objs = await session.execute(
            select(Dish)
            .join(Submenu, Submenu.id == Dish.submenu_id)
            .where(Dish.submenu_id == submenu_id, Submenu.menu_id == menu_id)
        )
        return db_objs.scalars().all()

    async def create(
        self,
        submenu_id: uuid.UUID,
        obj_in: DishCreate,
        session: AsyncSession
    ) -> Dish:
        """Создание объекта."""
        obj_in_data = obj_in.model_dump()
        db_obj = Dish(**obj_in_data, submenu_id=submenu_id)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Optional[Dish]:
        """Получение объекта по UUID."""
        dish = await session.execute(
            select(Dish)
            .join(Submenu, Submenu.id == Dish.submenu_id)
            .where(
                Dish.id == obj_id,
                Dish.submenu_id == submenu_id,
                Submenu.menu_id == menu_id
            )
        )
        return dish.scalars().first()

    async def get_or_404(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Optional[Dish]:
        obj = await self.get(menu_id, submenu_id, obj_id, session)
        if obj is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='dish not found'
            )
        return obj


dish_crud = CRUDDish(Dish)