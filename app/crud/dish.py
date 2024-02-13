import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_types import DishDiscountDict
from app.core.db import get_async_session
from app.core.redis_cache import DISCOUNT_PREFIX, cache
from app.crud.base import CRUDBase
from app.models import Dish, Submenu
from app.schemas.dish import DishCreate, DishUpdate


class CRUDDish(
    CRUDBase[Dish, DishCreate, DishUpdate]
):
    """Класс CRUD-операций для модели Dish."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_async_session)
    ) -> None:
        self.model = Dish
        self.session = session

    async def get_multi_filtered(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID
    ) -> list[DishDiscountDict]:
        """Получение списка отфильтрованных по `menu_id` и `submenu_id` объектов."""
        db_objs = await self.session.execute(
            select(Dish)
            .join(Submenu, Submenu.id == Dish.submenu_id)
            .where(Dish.submenu_id == submenu_id, Submenu.menu_id == menu_id)
        )
        dishes: list[DishDiscountDict] = []
        for dish in db_objs.scalars():
            discount = await cache.get(f'{DISCOUNT_PREFIX}:{menu_id}:{submenu_id}:{dish.id}')
            discount = discount or 0
            dishes.append(
                {
                    'id': dish.id,
                    'title': dish.title,
                    'description': dish.description,
                    'price': dish.price * (1 - discount),
                    'discount': f'{(discount * 100):.0f}%',
                    'submenu_id': dish.submenu_id
                }
            )
        return dishes

    async def get_filtered_discounted(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        obj_id: uuid.UUID
    ) -> DishDiscountDict | None:
        """
        Получение объекта по id, если он связан с соответствующими меню и субменю.

        Добавляется поле `discount`. Цена отображается со скидкой.
        """
        dish = await self.session.execute(
            select(Dish)
            .join(Submenu, Submenu.id == Dish.submenu_id)
            .where(
                Dish.id == obj_id,
                Dish.submenu_id == submenu_id,
                Submenu.menu_id == menu_id
            )
        )
        dish = dish.scalars().first()
        if dish is None:
            return None
        discount = await cache.get(f'{DISCOUNT_PREFIX}:{menu_id}:{submenu_id}:{dish.id}')
        discount = discount or 0
        return {
            'id': dish.id,
            'title': dish.title,
            'description': dish.description,
            'price': dish.price * (1 - discount),
            'discount': f'{(discount * 100):.0f}%',
            'submenu_id': dish.submenu_id
        }

    async def get_filtered_discounted_or_404(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        obj_id: uuid.UUID
    ) -> DishDiscountDict:
        """
        Получение объекта по id, если он связан с соответствующими меню и субменю.

        Добавляется поле `discount`. Цена отображается со скидкой.
        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_filtered_discounted(menu_id, submenu_id, obj_id)
        return self._exists_or_404(obj, detail='dish not found')

    async def get_filtered(
        self,
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        obj_id: uuid.UUID
    ) -> Dish | None:
        """Получение объекта по id, если он связан с соответствующими меню и субменю."""
        dish = await self.session.execute(
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
        obj_id: uuid.UUID
    ) -> Dish:
        """
        Получение объекта по id, если он связан с соответствующими меню и субменю.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get_filtered(menu_id, submenu_id, obj_id)
        return self._exists_or_404(obj, detail='dish not found')
