from typing import Any

import pandas

from app.core.config import settings
from app.core.constants import BASE_DIR
from app.core.exceptions import IncorrectTableError
from app.core.redis_cache import DISCOUNT_PREFIX, cache
from app.crud import dish_crud, menu_crud, submenu_crud
from app.schemas.dish import DishCreate, DishUpdate
from app.schemas.menu import MenuCreate, MenuUpdate
from app.schemas.submenu import SubmenuCreate, SubmenuUpdate
from app.schemas.table import DishTable, MenuTable, SubmenuTable
from app.services import google_service


def get_table_data():
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


async def delete_inconsistent_db_data(table_data, db_data, session):
    for db_menu in db_data:

        table_menu = None
        for menu in table_data:
            if menu.title == db_menu.title:
                table_menu = menu
                break
        if table_menu is None:
            await menu_crud.remove(db_menu, session)
            await cache.invalidate_on_menu_delete(db_menu.id)
            continue

        for db_submenu in db_menu.submenus:
            table_submenu = None
            for submenu in table_menu.submenus:
                if submenu.title == db_submenu.title:
                    table_submenu = submenu
                    break
            if table_submenu is None:
                await submenu_crud.remove(db_submenu, session)
                await cache.invalidate_on_submenu_delete(db_menu.id, db_submenu.id)
                continue

            for db_dish in db_submenu.dishes:
                table_dish = None
                for dish in table_submenu.dishes:
                    if dish.title == db_dish.title:
                        table_dish = dish
                        break
                if table_dish is None:
                    await dish_crud.remove(db_dish, session)
                    await cache.invalidate_on_dish_delete(db_menu.id, db_submenu.id, db_dish.id)


async def update_db_data(table_data, db_data, session):
    for table_menu in table_data:
        db_menu = None
        menu_created = False
        for menu in db_data:
            if menu.title == table_menu.title:
                db_menu = menu
                break
        if db_menu is None:
            db_menu = await menu_crud.create(
                MenuCreate(
                    title=table_menu.title,
                    description=table_menu.description
                ),
                session
            )
            await cache.invalidate_on_menu_create()
            menu_created = True
        else:
            if table_menu.description != db_menu.description:
                await menu_crud.update(
                    db_menu,
                    MenuUpdate(description=table_menu.description),
                    session
                )
                await cache.invalidate_on_menu_update(db_menu.id)

        await _update_db_submenus(table_menu, db_menu, menu_created, session)


def _is_menu(row: list[str]) -> bool:
    return bool(row[1] and row[2] and not row[3])


def _is_submenu(row: list[str]) -> bool:
    return bool(row[2] and row[3] and not row[4])


def _is_dish(row: list[str]) -> bool:
    return bool(row[3] and row[4] and row[5])


def _check_table_data(data: list[list[Any]]) -> None:
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


async def _update_db_submenus(table_menu, db_menu, menu_created, session):
    for table_submenu in table_menu.submenus:
        db_submenu = None
        submenu_created = False
        if menu_created is False:
            for submenu in db_menu.submenus:
                if submenu.title == table_submenu.title:
                    db_submenu = submenu
                    break
        if db_submenu is None:
            db_submenu = await submenu_crud.create(
                SubmenuCreate(
                    title=table_submenu.title,
                    description=table_submenu.description
                ),
                session,
                menu_id=db_menu.id
            )
            await cache.invalidate_on_submenu_create(db_menu.id)
            submenu_created = True
        else:
            if table_submenu.description != db_submenu.description:
                await submenu_crud.update(
                    db_submenu,
                    SubmenuUpdate(description=table_submenu.description),
                    session
                )
                await cache.invalidate_on_submenu_update(db_menu.id, db_submenu.id)
        await _update_db_dishes(table_submenu, db_menu, db_submenu, submenu_created, session)


async def _update_db_dishes(table_submenu, db_menu, db_submenu, submenu_created, session):
    for table_dish in table_submenu.dishes:
        db_dish = None
        if submenu_created is False:
            for dish in db_submenu.dishes:
                if dish.title == table_dish.title:
                    db_dish = dish
                    break
        if db_dish is None:
            await dish_crud.create(
                DishCreate(
                    title=table_dish.title,
                    description=table_dish.description,
                    price=table_dish.price
                ),
                session,
                submenu_id=db_submenu.id
            )
            await cache.invalidate_on_dish_create(db_menu.id, db_submenu.id)
            if table_dish.discount:
                await cache.set(
                    f'{DISCOUNT_PREFIX}:{db_menu.id}:{db_submenu.id}:{db_dish.id}',
                    table_dish.discount,
                    lifetime=False
                )
        else:
            to_update = {}
            if table_dish.description != db_dish.description:
                to_update['description'] = table_dish.description
            if float(table_dish.price) != db_dish.price:
                to_update['price'] = table_dish.price
            if to_update:
                await dish_crud.update(
                    db_dish,
                    DishUpdate.model_validate(to_update),
                    session
                )
            cache_discount = await cache.get(f'{DISCOUNT_PREFIX}:{db_menu.id}:{db_submenu.id}:{db_dish.id}')
            if table_dish.discount and table_dish.discount != cache_discount:
                await cache.set(
                    f'{DISCOUNT_PREFIX}:{db_menu.id}:{db_submenu.id}:{db_dish.id}',
                    table_dish.discount,
                    lifetime=False
                )
            if to_update or table_dish.discount and table_dish.discount != cache_discount:
                await cache.invalidate_on_dish_update(db_menu.id, db_submenu.id, db_dish.id)
