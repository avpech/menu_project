import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Dish, Submenu
from app.schemas.dish import DishCreate, DishUpdate


class CRUDDish(
    CRUDBase[Dish, DishCreate, DishUpdate]
):
    """Класс CRUD-операций для модели Dish."""

    async def get_multi_filtered(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        session: AsyncSession
    ) -> list[Dish]:
        """Получение списка отфильтрованных по `menu_id` и `submenu_id` объектов."""
        db_objs = await session.execute(
            select(Dish)
            .join(Submenu, Submenu.id == Dish.submenu_id)
            .where(Dish.submenu_id == submenu_id, Submenu.menu_id == menu_id)
        )
        return db_objs.scalars().all()

    async def get_filtered(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Dish | None:
        """Получение объекта по id, если он связан с соответствующими меню и субменю."""
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

    async def get_filtered_or_404(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Dish:
        """
        Получение объекта по id, если он связан с соответствующими меню и субменю.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_filtered(menu_id, submenu_id, obj_id, session)
        obj = self._exists_or_404(obj, detail='dish not found')
        return obj


dish_crud = CRUDDish(Dish)
