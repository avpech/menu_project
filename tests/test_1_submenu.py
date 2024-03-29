from http import HTTPStatus
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from .conftest import Menu, Submenu, TestingSessionLocal
from .constants import (
    CREATE_SUBMENU,
    DELETE_SUBMENU,
    GET_ALL_SUBMENUS,
    GET_SUBMENU,
    SUBMENU_OBJ_URL,
    SUBMENUS_URL,
    UNEXISTING_UUID,
    UPDATE_SUBMENU,
)
from .utils import reverse


class TestGetAllSubmenus:

    async def test_submenu_get_empty_list(
        self,
        client: AsyncClient,
        menu: Menu
    ):
        url = reverse(GET_ALL_SUBMENUS, menu_id=menu.id)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос к `{SUBMENUS_URL}` должен возвращать '
            'статус 200 (случай, когда в базе отсутствуют субменю)'
        )
        assert response.json() == [], (
            f'GET-запрос к `{SUBMENUS_URL}` должен возвращать '
            'пустой список, когда в базе отсутствуют субменю'
        )

    async def test_submenu_get_list(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(GET_ALL_SUBMENUS, menu_id=menu.id)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос к `{SUBMENUS_URL}` должен возвращать статус 200 '
            '(случай, когда в базе присутствуют субменю)'
        )
        assert response.json() != [], (
            f'GET-запрос к `{SUBMENUS_URL}` не должен возвращать пустой список, '
            'когда в базе присутствуют субменю'
        )


class TestCreateSubmenu:

    async def test_submenu_post_status(
        self,
        client: AsyncClient,
        menu: Menu
    ):
        url = reverse(CREATE_SUBMENU, menu_id=menu.id)
        json = {
            'title': 'submenu_title',
            'description': 'submenu_description'
        }
        response = await client.post(url, json=json)
        assert response.status_code == HTTPStatus.CREATED, (
            f'POST-запрос к `{SUBMENUS_URL}` должен возвращать статус 201'
        )

    async def test_submenu_post_object_created(
        self,
        client: AsyncClient,
        menu: Menu
    ):
        url = reverse(CREATE_SUBMENU, menu_id=menu.id)
        json = {
            'title': 'submenu_title',
            'description': 'submenu_description'
        }
        async with TestingSessionLocal() as session:
            before_count = await session.scalar(
                select(func.count(Submenu.id))
            )
            await client.post(url, json=json)
            after_count = await session.scalar(
                select(func.count(Submenu.id))
            )
        assert after_count == before_count + 1, (
            f'Убедитесь, что в результате POST-запроса к `{SUBMENUS_URL}` '
            'в базе создается новое субменю'
        )

    @pytest.mark.parametrize('field', ['title', 'description'])
    async def test_submenu_post_data(
        self,
        client: AsyncClient,
        field: str,
        menu: Menu
    ):
        url = reverse(CREATE_SUBMENU, menu_id=menu.id)
        json = {
            'title': 'submenu_title',
            'description': 'submenu_description'
        }
        response = await client.post(url, json=json)
        assert response.json().get(field) == json[field], (
            f'POST-запрос к `{SUBMENUS_URL}` должен возвращать '
            f'корректное значение поля `{field}`'
        )

    async def test_submenu_relation(
        self,
        client: AsyncClient,
        menu: Menu
    ):
        url = reverse(CREATE_SUBMENU, menu_id=menu.id)
        json = {
            'title': 'submenu_title',
            'description': 'submenu_description'
        }
        response = await client.post(url, json=json)
        assert response.json().get('menu_id') == str(menu.id), (
            f'В результате POST-запроса к `{SUBMENUS_URL}` '
            'должно создаваться субменю с полем `menu_id`, '
            'равным `menu_id` из `url`'
        )

    @pytest.mark.parametrize('submenu_title', [None, True, 123])
    async def test_submenu_post_invalid_title(
        self,
        client: AsyncClient,
        submenu_title: Any,
        menu: Menu
    ):
        url = reverse(CREATE_SUBMENU, menu_id=menu.id)
        json = {
            'title': submenu_title,
            'description': 'submenu_description'
        }
        response = await client.post(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'POST-запрос к `{SUBMENUS_URL}` с невалидным полем `title` '
            'в теле запроса должен возвращать статус 422'
        )

    @pytest.mark.parametrize('submenu_description', [None, True, 123])
    async def test_submenu_post_invalid_description(
        self,
        client: AsyncClient,
        submenu_description: Any,
        menu: Menu
    ):
        url = reverse(CREATE_SUBMENU, menu_id=menu.id)
        json = {
            'title': 'title',
            'description': submenu_description
        }
        response = await client.post(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'POST-запрос к `{SUBMENUS_URL}` с невалидным полем `description` '
            'в теле запроса должен возвращать статус 422'
        )

    @pytest.mark.parametrize('field', ['title', 'description'])
    async def test_submenu_post_missing_field(
        self,
        client: AsyncClient,
        field: str,
        menu: Menu
    ):
        url = reverse(CREATE_SUBMENU, menu_id=menu.id)
        json = {
            'title': 'submenu_title',
            'description': 'submenu_description'
        }
        del json[field]
        response = await client.post(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'POST-запрос к `{SUBMENUS_URL}` с отсутствующим полем `{field}` '
            'должен возвращать статус 422'
        )


class TestGetSubmenu:

    async def test_submenu_get_status(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(GET_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос к `{SUBMENU_OBJ_URL}` должен возвращать статус 200, '
            'если субменю с `id` равным `submenu_id` существует в базе'
        )

    async def test_submenu_get_404(
        self,
        client: AsyncClient,
        menu: Menu
    ):
        url = reverse(GET_SUBMENU, menu_id=menu.id, submenu_id=UNEXISTING_UUID)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'GET-запрос к `{SUBMENU_OBJ_URL}` должен возвращать статус 404, '
            'если субменю с `submenu_id` отсутствует в базе'
        )

    async def test_submenu_get_if_menu_404(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(GET_SUBMENU, menu_id=UNEXISTING_UUID, submenu_id=submenu.id)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'GET-запрос к `{SUBMENU_OBJ_URL}` должен возвращать статус 404, '
            'если меню с `menu_id` отсутствует в базе'
        )

    @pytest.mark.parametrize('field', ['title', 'description'])
    async def test_submenu_get_data(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu,
        field: str
    ):
        url = reverse(GET_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        response = await client.get(url)
        assert response.json().get(field) == getattr(submenu, field, None), (
            f'GET-запрос к `{SUBMENU_OBJ_URL}` '
            f'должен возвращать корректное значение поля `{field}`'
        )

    async def test_submenu_get_menu_id(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(GET_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        response = await client.get(url)
        assert response.json().get('menu_id') == str(menu.id), (
            f'GET-запрос к `{SUBMENU_OBJ_URL}` должен возвращать '
            'корректное значение поля `menu_id` '
            '(равное значению поля `menu_id` из `url`)'
        )


class TestUpdateSubmenu:

    async def test_submenu_patch_status(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(UPDATE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        json = {
            'title': 'submenu_title_changed',
            'description': 'submenu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.OK, (
            f'PATCH-запрос к `{SUBMENU_OBJ_URL}` должен возвращать '
            'статус 200, если субменю с `submenu_id` существует в базе'
        )

    async def test_submenu_patch_404(
        self,
        client: AsyncClient,
        menu: Menu
    ):
        url = reverse(UPDATE_SUBMENU, menu_id=menu.id, submenu_id=UNEXISTING_UUID)
        json = {
            'title': 'menu_title_changed',
            'description': 'menu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'PATCH-запрос к `{SUBMENU_OBJ_URL}` должен возвращать статус 404, '
            'если субменю с `submenu_id` отсутствует в базе'
        )

    async def test_submenu_patch_if_menu_404(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(UPDATE_SUBMENU, menu_id=UNEXISTING_UUID, submenu_id=submenu.id)
        json = {
            'title': 'menu_title_changed',
            'description': 'menu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'PATCH-запрос к `{SUBMENU_OBJ_URL}` должен возвращать статус 404, '
            'если меню с `menu_id` отсутствует в базе'
        )

    @pytest.mark.parametrize('field', ['title', 'description'])
    async def test_submenu_patch_data(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu,
        field: str
    ):
        url = reverse(UPDATE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        json = {
            'title': 'submenu_title_changed',
            'description': 'submenu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.json().get(field) == json[field], (
            f'PATCH-запрос к `{SUBMENU_OBJ_URL}` '
            f'должен возвращать корректное значение поля `{field}`'
        )

    @pytest.mark.parametrize('submenu_title', [None, True, 123])
    async def test_submenu_patch_invalid_title(
        self,
        client: AsyncClient,
        submenu_title: Any,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(UPDATE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        json = {
            'title': submenu_title,
            'description': 'menu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'PATCH-запрос к `{SUBMENU_OBJ_URL}` с невалидным полем `title` '
            'в теле запроса должен возвращать статус 422'
        )

    @pytest.mark.parametrize('submenu_description', [None, True, 123])
    async def test_submenu_patch_invalid_description(
        self,
        client: AsyncClient,
        submenu_description: Any,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(UPDATE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        json = {
            'title': 'menu_title_changed',
            'description': submenu_description
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'PATCH-запрос к `{SUBMENU_OBJ_URL}` с невалидным '
            'полем `description` в теле запроса должен возвращать статус 422'
        )


class TestDeleteSubmenu:

    async def test_submenu_delete_status(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(DELETE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        response = await client.delete(url)
        assert response.status_code == HTTPStatus.OK, (
            f'DELETE-запрос к `{SUBMENU_OBJ_URL}` должен возвращать статус 200, '
            'если субменю с `submenu_id` существует в базе'
        )

    async def test_submenu_delete_404(
        self,
        client: AsyncClient,
        menu: Menu
    ):
        url = reverse(DELETE_SUBMENU, menu_id=menu.id, submenu_id=UNEXISTING_UUID)
        response = await client.delete(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'DELETE-запрос к `{SUBMENU_OBJ_URL}` должен возвращать статус 404, '
            'если субменю с `submenu_id` отсутствует в базе'
        )

    async def test_submenu_delete_if_menu_404(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(DELETE_SUBMENU, menu_id=UNEXISTING_UUID, submenu_id=submenu.id)
        response = await client.delete(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'DELETE-запрос к `{SUBMENU_OBJ_URL}` должен возвращать статус 404, '
            'если меню с `menu_id` отсутствует в базе'
        )

    async def test_submenu_delete_object_deleted(
        self,
        client: AsyncClient,
        menu: Menu,
        submenu: Submenu
    ):
        url = reverse(DELETE_SUBMENU, menu_id=menu.id, submenu_id=submenu.id)
        await client.delete(url)
        async with TestingSessionLocal() as session:
            submenu_exists = await session.scalar(
                select(True).where(
                    (select(Submenu).where(Submenu.id == submenu.id)).exists()
                )
            )
        assert submenu_exists is None, (
            f'Убедитесь, что в результате DELETE-запроса к `{SUBMENU_OBJ_URL}` '
            'субменю с `id` равным `submenu_id` удаляется из базы'
        )
