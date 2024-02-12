import uuid

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.custom_types import MenuAnnotatedDict, MenuNestedSubmenusDict
from app.core.redis_cache import DISCOUNT_PREFIX, cache
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
        """Получение списка объектов с аннотациями."""
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

    async def get_all(
        self,
        session: AsyncSession
    ) -> list[MenuNestedSubmenusDict]:
        """Получение списка меню с вложенными подменю и блюдами."""
        dish_subq = (
            select(
                Dish.submenu_id,
                func.array_agg(
                    func.jsonb_build_object(
                        'id', Dish.id,
                        'title', Dish.title,
                        'description', Dish.description,
                        'price', Dish.price,
                        'submenu_id', Dish.submenu_id
                    )
                ).label('dishes')
            )
            .group_by(Dish.submenu_id)
            .subquery()
        )
        submenu_subq = (
            select(
                Submenu.menu_id,
                func.array_agg(
                    func.jsonb_build_object(
                        'id', Submenu.id,
                        'title', Submenu.title,
                        'description', Submenu.description,
                        'menu_id', Submenu.menu_id,
                        'dishes', func.coalesce(dish_subq.c.dishes, [])
                    )
                ).label('submenus')
            )
            .join(dish_subq, Submenu.id == dish_subq.c.submenu_id, isouter=True)
            .group_by(Submenu.menu_id)
            .subquery()
        )
        db_objs = await session.execute(
            select(
                func.jsonb_build_object(
                    'id', Menu.id,
                    'title', Menu.title,
                    'description', Menu.description,
                    'submenus', func.coalesce(submenu_subq.c.submenus, [])
                )
            )
            .join(submenu_subq, Menu.id == submenu_subq.c.menu_id, isouter=True)
            .group_by(Menu.id, submenu_subq.c.submenus)
        )
        menus = db_objs.scalars().all()
        for menu in menus:
            for submenu in menu['submenus']:
                for dish in submenu['dishes']:
                    discount = await cache.get(f'{DISCOUNT_PREFIX}:{menu["id"]}:{submenu["id"]}:{dish["id"]}')
                    discount = discount or 0
                    dish['price'] = dish['price'] * (1 - discount)
                    dish['discount'] = f'{(discount * 100):.0f}%'
        return menus

    async def get_all_objects(
        self,
        session: AsyncSession
    ) -> list[Menu]:
        """
        Получение списка меню (экземпляров `Menu`) с присоединенными
        (eager loaded) подменю и блюдами.
        """
        db_objs = await session.execute(
            select(Menu).options(joinedload(Menu.submenus).joinedload(Submenu.dishes))
        )
        return db_objs.unique().scalars().all()


menu_crud = CRUDMenu(Menu)
