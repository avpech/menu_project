from http import HTTPStatus

from httpx import AsyncClient

from tests.constants import (
    DELETE_MENU,
    DELETE_SUBMENU,
    GET_ALL_DISHES,
    GET_ALL_MENUS,
    GET_ALL_SUBMENUS,
    GET_MENU,
    GET_SUBMENU,
    MENU_OBJ_URL,
    SUBMENU_OBJ_URL,
)
from tests.utils import reverse


async def test_menu_get_count_dishes_and_submenus(
    client: AsyncClient, menu, submenu, dish, dish_another
):
    """
    Проверка подсчета количества подменю и блюд при просморе меню.

    В фикстурах меню, субменю и два блюда.
    """
    url = reverse(GET_MENU, menu_id=menu.id)
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('submenus_count') == 1, (
        'Проверьте правильность подсчета количества подменю '
        f'при GET-запросе к {MENU_OBJ_URL}'
    )
    assert response.json().get('dishes_count') == 2, (
        'Проверьте правильность подсчета количества блюд '
        f'при GET-запросе к {MENU_OBJ_URL}'
    )


async def test_submenu_get_count_dishes(
    client: AsyncClient, menu, submenu, dish, dish_another
):
    """
    Проверка подсчета количества подменю и блюд при просморе субменю.

    В фикстурах меню, субменю и два блюда.
    """
    url = reverse(GET_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert response.json().get('dishes_count') == 2, (
        'Проверьте правильность подсчета количества блюд '
        f'при GET-запросе к {SUBMENU_OBJ_URL}'
    )


async def test_submenus_list_after_delete_submenu(
    client: AsyncClient, menu, submenu, dish, dish_another
):
    """
    Проверка корректности удаления субменю.

    В фикстурах меню, субменю и два блюда.
    """
    submenu_url = reverse(DELETE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
    response = await client.delete(submenu_url)
    assert response.status_code == HTTPStatus.OK
    submenu_list_url = reverse(GET_ALL_SUBMENUS, menu_id=menu.id)
    response = await client.get(submenu_list_url)
    assert response.json() == [], (
        f'Проверьте, что после DELETE-запроса к {SUBMENU_OBJ_URL} '
        'подменю удаляется из базы'
    )


async def test_dishes_list_after_delete_submenu(
    client: AsyncClient, menu, submenu, dish, dish_another
):
    """
    Проверка удаления связанных с субменю блюд после удаления субменю.

    В фикстурах меню, субменю и два блюда.
    """
    submenu_url = reverse(DELETE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
    response = await client.delete(submenu_url)
    assert response.status_code == HTTPStatus.OK
    dishes_list_url = reverse(GET_ALL_DISHES, menu_id=menu.id, submenu_id=submenu.id)
    response = await client.get(dishes_list_url)
    assert response.json() == [], (
        f'Проверьте, что после DELETE-запроса к {SUBMENU_OBJ_URL} '
        'удаляются все связанные с удаленным субменю блюда'
    )


async def test_menu_dishes_and_submenus_count_after_delete_submenu(
    client: AsyncClient, menu, submenu, dish, dish_another
):
    """
    Проверка корректности подсчета количества субменю и блюд
    при просмотре меню после их удаления.

    В фикстурах меню, субменю и два блюда.
    """
    submenu_url = reverse(DELETE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
    response = await client.delete(submenu_url)
    assert response.status_code == HTTPStatus.OK
    menu_url = reverse(GET_MENU, menu_id=menu.id)
    response = await client.get(menu_url)
    assert response.json().get('submenus_count') == 0, (
        f'Проверьте, что при GET-запросе к {MENU_OBJ_URL} значение '
        '`submenus_count` равняется нулю для меню, не имеющих подменю'
    )
    assert response.json().get('dishes_count') == 0, (
        f'Проверьте, что при GET-запросе к {MENU_OBJ_URL} значение '
        '`dishes_count` равняется нулю для меню, не имеющих подменю'
    )


async def test_menu_list_after_menu_delete(
    client: AsyncClient, menu, submenu, dish, dish_another
):
    """Проверка корректности удаления меню."""
    menu_url = reverse(DELETE_MENU, menu_id=menu.id)
    response = await client.delete(menu_url)
    assert response.status_code == HTTPStatus.OK
    menu_list_url = reverse(GET_ALL_MENUS)
    response = await client.get(menu_list_url)
    assert response.json() == [], (
        f'Проверьте, что после DELETE-запроса к {MENU_OBJ_URL} '
        'меню удаляется из базы'
    )
