from httpx import AsyncClient
from http import HTTPStatus
import pytest
from conftest import UNEXISTING_UUID, TestingSessionLocal
from sqlalchemy import select, func
from conftest import Menu, Submenu, Dish




async def test_menu_get_empty_list(client: AsyncClient):
    url = '/api/v1/menus/'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'GET-запрос к `{url}` должен возвращать статус 200 '
        '(случай, когда в базе отсутствуют меню)'
    )
    assert response.json() == [], (
        f'GET-запрос к `{url}` должен возвращать пустой список, '
        'когда в базе отсутствуют меню'
    )


async def test_menu_post_status(client: AsyncClient):
    url = '/api/v1/menus/'
    json = {
        'title': 'menu_title',
        'description': 'menu_description'
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.CREATED, (
        f'POST-запрос к `{url}` должен возвращать статус 201'
    )


async def test_menu_post_object_created(client: AsyncClient):
    url = '/api/v1/menus/'
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
        f'`{url}` в базе создается новое меню'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_menu_post_data(client: AsyncClient, field):
    url = '/api/v1/menus/'
    json = {
        'title': 'menu_title',
        'description': 'menu_description'
    }
    response = await client.post(url, json=json)
    assert response.json().get(field) == json[field], (
        f'POST-запрос к `{url}` должен возвращать '
        f'корректное значение поля `{field}`'
    )


@pytest.mark.parametrize('menu_title', [None, True, 123])
async def test_menu_post_invalid_title(client: AsyncClient, menu_title):
    url = '/api/v1/menus/'
    json = {
        'title': menu_title,
        'description': 'descr'
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'POST-запрос к `{url}` с невалидным полем `title` '
        'в теле запроса должен возвращать статус 422'
    )


@pytest.mark.parametrize('menu_description', [None, True, 123])
async def test_menu_post_invalid_description(client: AsyncClient, menu_description):
    url = '/api/v1/menus/'
    json = {
        'title': 'title',
        'description': menu_description
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'POST-запрос к `{url}` с невалидным полем `description` '
        'в теле запроса должен возвращать статус 422'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_menu_post_missing_field(client: AsyncClient, field):
    url = '/api/v1/menus/'
    json = {
        'title': 'menu_title',
        'description': 'menu_description'
    }
    del json[field]
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'POST-запрос к `{url}` с отсутствующим полем `{field}` '
        'должен возвращать статус 422'
    )


async def test_menu_get_list(client: AsyncClient, menu):
    url = '/api/v1/menus/'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'GET-запрос к `{url}` должен возвращать статус 200 '
        '(случай, когда в базе присутствуют меню)'
    )
    assert response.json() != [], (
        f'GET-запрос к `{url}` не должен возвращать пустой список, '
        'когда в базе присутствуют меню'
    )


async def test_menu_get_status(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'GET-запрос к `/api/v1/menus/menu_id/` должен возвращать '
        'статус 200, если меню с `id` равным `menu_id` существует в базе'
    )


async def test_menu_get_404(client: AsyncClient):
    url = f'/api/v1/menus/{UNEXISTING_UUID}'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'GET-запрос к `/api/v1/menus/menu_id/` должен возвращать '
        'статус 404, если меню с `menu_id` отсутствует в базе'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_menu_get_data(client: AsyncClient, menu, field):
    url = f'/api/v1/menus/{menu.id}'
    response = await client.get(url)
    assert response.json().get(field) == getattr(menu, field, None), (
        'GET-запрос к `/api/v1/menus/menu_id/` должен возвращать '
        f'корректное значение поля `{field}`'
    )


async def test_menu_patch_status(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}'
    json = {
        'title': 'menu_title_changed',
        'description': 'menu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.OK, (
        'PATCH-запрос к `/api/v1/menus/menu_id/` должен возвращать '
        'статус 200, если меню с `menu_id` существует в базе'
    )


async def test_menu_patch_404(client: AsyncClient):
    url = f'/api/v1/menus/{UNEXISTING_UUID}'
    json = {
        'title': 'menu_title_changed',
        'description': 'menu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'PATCH-запрос к `/api/v1/menus/menu_id/` должен возвращать '
        'статус 404, если меню с `menu_id` отсутствует в базе'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_menu_patch_data(client: AsyncClient, menu, field):
    url = f'/api/v1/menus/{menu.id}'
    json = {
        'title': 'menu_title_changed',
        'description': 'menu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.json().get(field) == json[field], (
        f'PATCH-запрос к `/api/v1/menus/menu_id/` должен возвращать '
        f'корректное значение поля `{field}`'
    )


@pytest.mark.parametrize('menu_title', [None, True, 123])
async def test_menu_patch_invalid_title(client: AsyncClient, menu_title, menu):
    url = f'/api/v1/menus/{menu.id}'
    json = {
        'title': menu_title,
        'description': 'menu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'PATCH-запрос к `/api/v1/menus/menu_id/` с невалидным полем `title` '
        'в теле запроса должен возвращать статус 422'
    )


@pytest.mark.parametrize('menu_description', [None, True, 123])
async def test_menu_patch_invalid_description(client: AsyncClient, menu_description, menu):
    url = f'/api/v1/menus/{menu.id}'
    json = {
        'title': 'menu_title_changed',
        'description': menu_description
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'PATCH-запрос к `/api/v1/menus/menu_id/` с невалидным полем '
        '`description` в теле запроса должен возвращать статус 422'
    )


async def test_menu_delete_status(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}'
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.OK, (
        'DELETE-запрос к `/api/v1/menus/menu_id/` должен возвращать '
        'статус 200, если меню с `menu_id` существует в базе'
    )


async def test_menu_delete_404(client: AsyncClient):
    url = f'/api/v1/menus/{UNEXISTING_UUID}'
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'DELETE-запрос к `/api/v1/menus/menu_id/` должен возвращать '
        'статус 404, если меню с `menu_id` отсутствует в базе'
    )


async def test_menu_delete_object_deleted(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}'
    await client.delete(url)
    async with TestingSessionLocal() as session:
        menu_exists = await session.scalar(
            select(True).where(
                (select(Menu).where(Menu.id == menu.id)).exists()
            )
        )
    assert menu_exists is None, (
        'Убедитесь, что в результате DELETE-запроса к '
        '`/api/v1/menus/menu_id/` меню с `id` равным `menu_id` '
        'удаляется из базы'
    )
