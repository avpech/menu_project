from httpx import AsyncClient
from http import HTTPStatus
import pytest
from conftest import UNEXISTING_UUID, TestingSessionLocal
from sqlalchemy import select, func
from conftest import Menu, Submenu, Dish




async def test_submenu_get_empty_list(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}/submenus'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus` должен возвращать '
        'статус 200 (случай, когда в базе отсутствуют субменю)'
    )
    assert response.json() == [], (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus` должен возвращать '
        'пустой список, когда в базе отсутствуют субменю'
    )


async def test_submenu_post_status(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}/submenus'
    json = {
        'title': 'submenu_title',
        'description': 'submenu_description'
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.CREATED, (
        'POST-запрос к `/api/v1/menus/<menu_id>/submenus` '
        'должен возвращать статус 201'
    )


async def test_submenu_post_object_created(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}/submenus'
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
        'Убедитесь, что в результате POST-запроса к '
        '`/api/v1/menus/<menu_id>/submenus` в базе создается новое субменю'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_submenu_post_data(client: AsyncClient, field, menu):
    url = f'/api/v1/menus/{menu.id}/submenus'
    json = {
        'title': 'submenu_title',
        'description': 'submenu_description'
    }
    response = await client.post(url, json=json)
    assert response.json().get(field) == json[field], (
        'POST-запрос к `/api/v1/menus/<menu_id>/submenus` '
        f'должен возвращать корректное значение поля `{field}`'
    )


async def test_submenu_relation(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}/submenus'
    json = {
        'title': 'submenu_title',
        'description': 'submenu_description'
    }
    response = await client.post(url, json=json)
    assert response.json().get('menu_id') == str(menu.id), (
        'В результате POST-запроса к `/api/v1/menus/<menu_id>/submenus` '
        'должно создаваться субменю с полем `menu_id`, '
        'равным `menu_id` из `url`'
    )


@pytest.mark.parametrize('submenu_title', [None, True, 123])
async def test_submenu_post_invalid_title(client: AsyncClient, submenu_title, menu):
    url = f'/api/v1/menus/{menu.id}/submenus'
    json = {
        'title': submenu_title,
        'description': 'submenu_description'
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'POST-запрос к `/api/v1/menus/<menu_id>/submenus` '
        'с невалидным полем `title` в теле запроса должен '
        'возвращать статус 422'
    )


@pytest.mark.parametrize('submenu_description', [None, True, 123])
async def test_submenu_post_invalid_description(client: AsyncClient, submenu_description, menu):
    url = f'/api/v1/menus/{menu.id}/submenus'
    json = {
        'title': 'title',
        'description': submenu_description
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'POST-запрос к `/api/v1/menus/<menu_id>/submenus` '
        'с невалидным полем `description` в теле запроса должен '
        'возвращать статус 422'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_submenu_post_missing_field(client: AsyncClient, field, menu):
    url = f'/api/v1/menus/{menu.id}/submenus'
    json = {
        'title': 'submenu_title',
        'description': 'submenu_description'
    }
    del json[field]
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'POST-запрос к `/api/v1/menus/<menu_id>/submenus` '
        f'с отсутствующим полем `{field}` должен возвращать статус 422'
    )


async def test_submenu_get_list(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{menu.id}/submenus'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus` '
        'должен возвращать статус 200 '
        '(случай, когда в базе присутствуют субменю)'
    )
    assert response.json() != [], (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus` '
        'не должен возвращать пустой список, '
        'когда в базе присутствуют субменю'
    )


async def test_submenu_get_status(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 200, если субменю с `id` равным '
        '`submenu_id` существует в базе'
    )


async def test_submenu_get_404(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}/submenus/{UNEXISTING_UUID}'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 404, если субменю с `submenu_id` '
        'отсутствует в базе'
    )


async def test_submenu_get_if_menu_404(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{UNEXISTING_UUID}/submenus/{submenu.id}'
    response = await client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 404, если меню с `menu_id` '
        'отсутствует в базе'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_submenu_get_data(client: AsyncClient, menu, submenu, field):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    response = await client.get(url)
    assert response.json().get(field) == getattr(submenu, field, None), (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        f'должен возвращать корректное значение поля `{field}`'
    )


async def test_submenu_get_menu_id(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    response = await client.get(url)
    assert response.json().get('menu_id') == str(menu.id), (
        'GET-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать корректное значение поля `menu_id` '
        '(равное значению поля `menu_id` из `url`)'
    )


async def test_submenu_patch_status(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    json = {
        'title': 'submenu_title_changed',
        'description': 'submenu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.OK, (
        'PATCH-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 200, если субменю с `submenu_id` '
        'существует в базе'
    )


async def test_submenu_patch_404(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}/submenus/{UNEXISTING_UUID}'
    json = {
        'title': 'menu_title_changed',
        'description': 'menu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'PATCH-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 404, если субменю с `submenu_id` '
        'отсутствует в базе'
    )


async def test_submenu_patch_if_menu_404(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{UNEXISTING_UUID}/submenus/{submenu.id}'
    json = {
        'title': 'menu_title_changed',
        'description': 'menu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'PATCH-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 404, если меню с `menu_id` '
        'отсутствует в базе'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_submenu_patch_data(client: AsyncClient, menu, submenu, field):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    json = {
        'title': 'submenu_title_changed',
        'description': 'submenu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.json().get(field) == json[field], (
        'PATCH-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        f'должен возвращать корректное значение поля `{field}`'
    )


@pytest.mark.parametrize('submenu_title', [None, True, 123])
async def test_submenu_patch_invalid_title(client: AsyncClient, submenu_title, menu, submenu):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    json = {
        'title': submenu_title,
        'description': 'menu_description_changed'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'PATCH-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'с невалидным полем `title` в теле запроса '
        'должен возвращать статус 422'
    )


@pytest.mark.parametrize('submenu_description', [None, True, 123])
async def test_submenu_patch_invalid_description(client: AsyncClient, submenu_description, menu, submenu):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    json = {
        'title': 'menu_title_changed',
        'description': submenu_description
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        'PATCH-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'с невалидным полем `description` в теле запроса '
        'должен возвращать статус 422'
    )


async def test_submenu_delete_status(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.OK, (
        'DELETE-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 200, если субменю '
        'с `submenu_id` существует в базе'
    )


async def test_submenu_delete_404(client: AsyncClient, menu):
    url = f'/api/v1/menus/{menu.id}/submenus/{UNEXISTING_UUID}'
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'DELETE-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 404, если субменю '
        'с `submenu_id` отсутствует в базе'
    )


async def test_submenu_delete_if_menu_404(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{UNEXISTING_UUID}/submenus/{submenu.id}'
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'DELETE-запрос к `/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'должен возвращать статус 404, если меню '
        'с `menu_id` отсутствует в базе'
    )


async def test_submenu_delete_object_deleted(client: AsyncClient, menu, submenu):
    url = f'/api/v1/menus/{menu.id}/submenus/{submenu.id}'
    await client.delete(url)
    async with TestingSessionLocal() as session:
        submenu_exists = await session.scalar(
            select(True).where(
                (select(Submenu).where(Submenu.id == submenu.id)).exists()
            )
        )
    assert submenu_exists is None, (
        'Убедитесь, что в результате DELETE-запроса к '
        '`/api/v1/menus/<menu_id>/submenus/<submenu_id>` '
        'субменю с `id` равным `submenu_id` удаляется из базы'
    )
