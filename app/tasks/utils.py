from typing import Any

import pandas

from app.core.config import settings
from app.core.constants import BASE_DIR
from app.core.custom_types import MenuNestedDict
from app.core.exceptions import IncorrectTableError
from app.core.redis_cache import DISCOUNT_PREFIX, cache
from app.crud.dish import CRUDDish
from app.crud.menu import CRUDMenu
from app.crud.submenu import CRUDSubmenu
from app.schemas.dish import DishCreate, DishUpdate
from app.schemas.menu import MenuCreate, MenuUpdate
from app.schemas.submenu import SubmenuCreate, SubmenuUpdate
from app.schemas.table import DishTable, MenuTable, SubmenuTable
from app.services import google_service


def get_table_data() -> list[MenuTable]:
    """Получение данных из таблицы."""
    data: Any
    if settings.use_google_sheets:
        data = google_service.read_values(settings.google_sheet_id)
    else:
        file_path = BASE_DIR / 'admin' / 'Menu.xlsx'
        data = pandas.read_excel(file_path, header=None)
        data.fillna('', inplace=True)
        data = data.values.tolist()
    for row in data:
        while len(row) < 7:
            row.append('')
    _check_table_data(data)
    table_data = []
    for row in data:
        if _is_menu(row):
            menu = MenuTable(title=row[1], description=row[2])
            table_data.append(menu)
        elif _is_submenu(row):
            submenu = SubmenuTable(title=row[2], description=row[3])
            menu.submenus.append(submenu)
        elif _is_dish(row):
            dish = DishTable(title=row[3], description=row[4], price=row[5], discount=row[6])
            submenu.dishes.append(dish)
    return table_data


def _is_menu(row: list[Any]) -> bool:
    """Проверка строки на то, что она описывает меню."""
    return bool(row[1] and row[2] and not row[3])


def _is_submenu(row: list[Any]) -> bool:
    """Проверка строки на то, что она описывает подменю."""
    return bool(row[2] and row[3] and not row[4])


def _is_dish(row: list[Any]) -> bool:
    """Проверка строки на то, что она описывает блюдо."""
    return bool(row[3] and row[4] and row[5])


def _check_table_data(data: list[list[Any]]) -> None:
    """Проверка структуры таблицы."""
    prev_menu = False
    if data and data[0] and not _is_menu(data[0]):
        raise IncorrectTableError(
            'Некорректная структура таблицы. Первая строка должна содержать меню.'
        )
    for row in data:
        if _is_menu(row) and not (row[3] or row[4] or row[5] or row[6]):
            prev_menu = True
            continue
        if _is_submenu(row) and not (row[0] or row[4] or row[5] or row[6]):
            prev_menu = False
            continue
        if _is_dish(row) and not (row[0] or row[1] or prev_menu):
            continue
        if not any(row):
            continue
        raise IncorrectTableError('Некорректная структура таблицы')


class SyncDatabaseData:
    """Класс для обновления данных в базе."""

    def __init__(
        self,
        menu_crud: CRUDMenu,
        submenu_crud: CRUDSubmenu,
        dish_crud: CRUDDish
    ) -> None:
        self.menu_crud = menu_crud
        self.submenu_crud = submenu_crud
        self.dish_crud = dish_crud

    async def delete_inconsistent_db_data(
        self,
        table_data: list[MenuTable],
        db_data: list[MenuNestedDict]
    ) -> None:
        """Удаление из бд данных, отсутствующих в таблице."""
        for db_menu in db_data:

            table_menu = None
            for menu in table_data:
                if menu.title == db_menu['title']:
                    table_menu = menu
                    break
            if table_menu is None:
                menu_obj: Any
                menu_obj = await self.menu_crud.get(db_menu['id'])
                await self.menu_crud.remove(menu_obj)
                await cache.invalidate_on_menu_delete(db_menu['id'])
                continue

            for db_submenu in db_menu['submenus']:
                table_submenu = None
                for submenu in table_menu.submenus:
                    if submenu.title == db_submenu['title']:
                        table_submenu = submenu
                        break
                if table_submenu is None:
                    submenu_obj: Any
                    submenu_obj = await self.submenu_crud.get(db_submenu['id'])
                    await self.submenu_crud.remove(submenu_obj)
                    await cache.invalidate_on_submenu_delete(db_menu['id'], db_submenu['id'])
                    continue

                for db_dish in db_submenu['dishes']:
                    table_dish = None
                    for dish in table_submenu.dishes:
                        if dish.title == db_dish['title']:
                            table_dish = dish
                            break
                    if table_dish is None:
                        dish_obj: Any
                        dish_obj = await self.dish_crud.get(db_dish['id'])
                        await self.dish_crud.remove(dish_obj)
                        await cache.invalidate_on_dish_delete(db_menu['id'], db_submenu['id'], db_dish['id'])

    async def update_db_data(
        self,
        table_data: list[MenuTable],
        db_data: list[MenuNestedDict]
    ) -> None:
        """Добавление в бд данных из таблицы."""
        for table_menu in table_data:
            db_menu: Any = None
            menu_created = False
            for menu in db_data:
                if menu['title'] == table_menu.title:
                    db_menu = menu
                    break
            if db_menu is None:
                db_menu_obj = await self.menu_crud.create(
                    MenuCreate(
                        title=table_menu.title,
                        description=table_menu.description
                    )
                )
                db_menu = {'id': db_menu_obj.id}
                await cache.invalidate_on_menu_create()
                menu_created = True
            else:
                if table_menu.description != db_menu['description']:
                    menu_obj: Any
                    menu_obj = await self.menu_crud.get(db_menu['id'])
                    await self.menu_crud.update(
                        menu_obj,
                        MenuUpdate(description=table_menu.description)
                    )
                    await cache.invalidate_on_menu_update(db_menu['id'])

            await self._update_db_submenus(table_menu, db_menu, menu_created)

    async def _update_db_submenus(
        self,
        table_menu: MenuTable,
        db_menu: Any,
        menu_created: bool
    ) -> None:
        """Добавление в бд данных о подменю из таблицы."""
        for table_submenu in table_menu.submenus:
            db_submenu = None
            submenu_created = False
            if menu_created is False:
                for submenu in db_menu['submenus']:
                    if submenu['title'] == table_submenu.title:
                        db_submenu = submenu
                        break
            if db_submenu is None:
                db_submenu_obj = await self.submenu_crud.create(
                    SubmenuCreate(
                        title=table_submenu.title,
                        description=table_submenu.description
                    ),
                    menu_id=db_menu['id']
                )
                db_submenu = {'id': db_submenu_obj.id}
                await cache.invalidate_on_submenu_create(db_menu['id'])
                submenu_created = True
            else:
                if table_submenu.description != db_submenu['description']:
                    submenu_obj: Any
                    submenu_obj = await self.submenu_crud.get(db_submenu['id'])
                    await self.submenu_crud.update(
                        submenu_obj,
                        SubmenuUpdate(description=table_submenu.description)
                    )
                    await cache.invalidate_on_submenu_update(db_menu['id'], db_submenu['id'])
            await self._update_db_dishes(table_submenu, db_menu, db_submenu, submenu_created)

    async def _update_db_dishes(
        self,
        table_submenu: SubmenuTable,
        db_menu: Any,
        db_submenu: Any,
        submenu_created: bool
    ) -> None:
        for table_dish in table_submenu.dishes:
            db_dish = None
            if submenu_created is False:
                for dish in db_submenu['dishes']:
                    if dish['title'] == table_dish.title:
                        db_dish = dish
                        break
            if db_dish is None:
                db_dish_obj = await self.dish_crud.create(
                    DishCreate(
                        title=table_dish.title,
                        description=table_dish.description,
                        price=str(table_dish.price)
                    ),
                    submenu_id=db_submenu['id']
                )
                db_dish = {'id': db_dish_obj.id}
                await cache.invalidate_on_dish_create(db_menu['id'], db_submenu['id'])
                if table_dish.discount:
                    await cache.set(
                        f'{DISCOUNT_PREFIX}:{db_menu["id"]}:{db_submenu["id"]}:{db_dish["id"]}',
                        table_dish.discount,
                        lifetime=False
                    )
            else:
                to_update = {}
                if table_dish.description != db_dish['description']:
                    to_update['description'] = table_dish.description
                if table_dish.price != db_dish['price']:
                    to_update['price'] = str(table_dish.price)
                if to_update:
                    dish_obj: Any
                    dish_obj = await self.dish_crud.get(db_dish['id'])
                    await self.dish_crud.update(
                        dish_obj,
                        DishUpdate.model_validate(to_update)
                    )
                cache_discount = await cache.get(
                    f'{DISCOUNT_PREFIX}:{db_menu["id"]}:{db_submenu["id"]}:{db_dish["id"]}'
                )
                if table_dish.discount and table_dish.discount != cache_discount:
                    await cache.set(
                        f'{DISCOUNT_PREFIX}:{db_menu["id"]}:{db_submenu["id"]}:{db_dish["id"]}',
                        table_dish.discount,
                        lifetime=False
                    )
                if to_update or table_dish.discount and table_dish.discount != cache_discount:
                    await cache.invalidate_on_dish_update(db_menu['id'], db_submenu['id'], db_dish['id'])
