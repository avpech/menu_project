from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from .conftest import Menu, TestingSessionLocal
from .constants import (
    CREATE_MENU,
    DELETE_MENU,
    GET_ALL_MENUS,
    GET_MENU,
    MENU_OBJ_URL,
    MENUS_URL,
    UNEXISTING_UUID,
    UPDATE_MENU,
)
from .utils import reverse


class TestGetAllMenus:

    async def test_menu_get_empty_list(self, client: AsyncClient):
        url = reverse(GET_ALL_MENUS)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос к `{MENUS_URL}` должен возвращать статус 200 '
            '(случай, когда в базе отсутствуют меню)'
        )
        assert response.json() == [], (
            f'GET-запрос к `{MENUS_URL}` должен возвращать пустой список, '
            'когда в базе отсутствуют меню'
        )

    async def test_menu_get_list(self, client: AsyncClient, menu):
        url = reverse(GET_ALL_MENUS)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос к `{MENUS_URL}` должен возвращать статус 200 '
            '(случай, когда в базе присутствуют меню)'
        )
        assert response.json() != [], (
            f'GET-запрос к `{MENUS_URL}` не должен возвращать пустой список, '
            'когда в базе присутствуют меню'
        )


class TestCreateMenu:

    async def test_menu_post_status(self, client: AsyncClient):
        url = reverse(CREATE_MENU)
        json = {
            'title': 'menu_title',
            'description': 'menu_description'
        }
        response = await client.post(url, json=json)
        assert response.status_code == HTTPStatus.CREATED, (
            f'POST-запрос к `{MENUS_URL}` должен возвращать статус 201'
        )

    async def test_menu_post_object_created(self, client: AsyncClient):
        url = reverse(CREATE_MENU)
        json = {
            'title': 'menu_title',
            'description': 'menu_description'
        }
        async with TestingSessionLocal() as session:
            before_count = await session.scalar(
                select(func.count(Menu.id))
            )
            await client.post(url, json=json)
            after_count = await session.scalar(
                select(func.count(Menu.id))
            )
        assert after_count == before_count + 1, (
            'Убедитесь, что в результате POST-запроса к '
            f'`{MENUS_URL}` в базе создается новое меню'
        )

    @pytest.mark.parametrize('field', ['title', 'description'])
    async def test_menu_post_data(self, client: AsyncClient, field):
        url = reverse(CREATE_MENU)
        json = {
            'title': 'menu_title',
            'description': 'menu_description'
        }
        response = await client.post(url, json=json)
        assert response.json().get(field) == json[field], (
            f'POST-запрос к `{MENUS_URL}` должен возвращать '
            f'корректное значение поля `{field}`'
        )

    @pytest.mark.parametrize('menu_title', [None, True, 123])
    async def test_menu_post_invalid_title(self, client: AsyncClient, menu_title):
        url = reverse(CREATE_MENU)
        json = {
            'title': menu_title,
            'description': 'descr'
        }
        response = await client.post(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'POST-запрос к `{MENUS_URL}` с невалидным полем `title` '
            'в теле запроса должен возвращать статус 422'
        )

    @pytest.mark.parametrize('menu_description', [None, True, 123])
    async def test_menu_post_invalid_description(self, client: AsyncClient, menu_description):
        url = reverse(CREATE_MENU)
        json = {
            'title': 'title',
            'description': menu_description
        }
        response = await client.post(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'POST-запрос к `{MENUS_URL}` с невалидным полем `description` '
            'в теле запроса должен возвращать статус 422'
        )

    @pytest.mark.parametrize('field', ['title', 'description'])
    async def test_menu_post_missing_field(self, client: AsyncClient, field):
        url = reverse(CREATE_MENU)
        json = {
            'title': 'menu_title',
            'description': 'menu_description'
        }
        del json[field]
        response = await client.post(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'POST-запрос к `{MENUS_URL}` с отсутствующим полем `{field}` '
            'должен возвращать статус 422'
        )


class TestGetMenu:

    async def test_menu_get_status(self, client: AsyncClient, menu):
        url = reverse(GET_MENU, menu_id=menu.id)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            f'GET-запрос к `{MENU_OBJ_URL}` должен возвращать '
            'статус 200, если меню с `id` равным `menu_id` существует в базе'
        )

    async def test_menu_get_404(self, client: AsyncClient):
        url = reverse(GET_MENU, menu_id=UNEXISTING_UUID)
        response = await client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'GET-запрос к `{MENU_OBJ_URL}` должен возвращать '
            'статус 404, если меню с `menu_id` отсутствует в базе'
        )

    @pytest.mark.parametrize('field', ['title', 'description'])
    async def test_menu_get_data(self, client: AsyncClient, menu, field):
        url = reverse(GET_MENU, menu_id=menu.id)
        response = await client.get(url)
        assert response.json().get(field) == getattr(menu, field, None), (
            f'GET-запрос к `{MENU_OBJ_URL}` должен возвращать '
            f'корректное значение поля `{field}`'
        )


class TestUpdateMenu:

    async def test_menu_patch_status(self, client: AsyncClient, menu):
        url = reverse(UPDATE_MENU, menu_id=menu.id)
        json = {
            'title': 'menu_title_changed',
            'description': 'menu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.OK, (
            f'PATCH-запрос к `{MENU_OBJ_URL}` должен возвращать '
            'статус 200, если меню с `menu_id` существует в базе'
        )

    async def test_menu_patch_404(self, client: AsyncClient):
        url = reverse(UPDATE_MENU, menu_id=UNEXISTING_UUID)
        json = {
            'title': 'menu_title_changed',
            'description': 'menu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'PATCH-запрос к `{MENU_OBJ_URL}` должен возвращать '
            'статус 404, если меню с `menu_id` отсутствует в базе'
        )

    @pytest.mark.parametrize('field', ['title', 'description'])
    async def test_menu_patch_data(self, client: AsyncClient, menu, field):
        url = reverse(UPDATE_MENU, menu_id=menu.id)
        json = {
            'title': 'menu_title_changed',
            'description': 'menu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.json().get(field) == json[field], (
            f'PATCH-запрос к `{MENU_OBJ_URL}` должен возвращать '
            f'корректное значение поля `{field}`'
        )

    @pytest.mark.parametrize('menu_title', [None, True, 123])
    async def test_menu_patch_invalid_title(self, client: AsyncClient, menu_title, menu):
        url = reverse(UPDATE_MENU, menu_id=menu.id)
        json = {
            'title': menu_title,
            'description': 'menu_description_changed'
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'PATCH-запрос к `{MENU_OBJ_URL}` с невалидным полем `title` '
            'в теле запроса должен возвращать статус 422'
        )

    @pytest.mark.parametrize('menu_description', [None, True, 123])
    async def test_menu_patch_invalid_description(self, client: AsyncClient, menu_description, menu):
        url = reverse(UPDATE_MENU, menu_id=menu.id)
        json = {
            'title': 'menu_title_changed',
            'description': menu_description
        }
        response = await client.patch(url, json=json)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
            f'PATCH-запрос к `{MENU_OBJ_URL}` с невалидным полем '
            '`description` в теле запроса должен возвращать статус 422'
        )


class TestDeleteMenu:

    async def test_menu_delete_status(self, client: AsyncClient, menu):
        url = reverse(DELETE_MENU, menu_id=menu.id)
        response = await client.delete(url)
        assert response.status_code == HTTPStatus.OK, (
            f'DELETE-запрос к `{MENU_OBJ_URL}` должен возвращать '
            'статус 200, если меню с `menu_id` существует в базе'
        )

    async def test_menu_delete_404(self, client: AsyncClient):
        url = reverse(DELETE_MENU, menu_id=UNEXISTING_UUID)
        response = await client.delete(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'DELETE-запрос к `{MENU_OBJ_URL}` должен возвращать '
            'статус 404, если меню с `menu_id` отсутствует в базе'
        )

    async def test_menu_delete_object_deleted(self, client: AsyncClient, menu):
        url = reverse(DELETE_MENU, menu_id=menu.id)
        await client.delete(url)
        async with TestingSessionLocal() as session:
            menu_exists = await session.scalar(
                select(True).where(
                    (select(Menu).where(Menu.id == menu.id)).exists()
                )
            )
        assert menu_exists is None, (
            'Убедитесь, что в результате DELETE-запроса к '
            f'`{MENU_OBJ_URL}` меню с `id` равным `menu_id` '
            'удаляется из базы'
        )
