from http import HTTPStatus

import pytest
from conftest import (DISH_OBJ_URL, DISHES_URL, UNEXISTING_UUID, Dish,
                      TestingSessionLocal)
from httpx import AsyncClient
from sqlalchemy import func, select


async def test_dish_get_empty_list(client: AsyncClient, menu, submenu):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'GET-запрос к `{DISHES_URL}` должен возвращать статус 200 '
        '(случай, когда в базе отсутствуют блюда)'
    )
    assert response.json() == [], (
        f'GET-запрос к `{DISHES_URL}` должен возвращать пустой '
        'список, когда в базе отсутствуют блюда'
    )


async def test_dish_post_status(client: AsyncClient, menu, submenu):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': 'dish_title',
        'description': 'dish_description',
        'price': '10.0'
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.CREATED, (
        f'POST-запрос к `{DISHES_URL}` должен возвращать статус 201'
    )


async def test_dish_post_object_created(client: AsyncClient, menu, submenu):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': 'dish_title',
        'description': 'dish_description',
        'price': '10.0'
    }
    async with TestingSessionLocal() as session:
        before_count = await session.scalar(
            select(func.count(Dish.id))
        )
        await client.post(url, json=json)
        after_count = await session.scalar(
            select(func.count(Dish.id))
        )
    assert after_count == before_count + 1, (
        f'Убедитесь, что в результате POST-запроса к `{DISHES_URL}` '
        'в базе создается новое блюдо'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_dish_post_data(client: AsyncClient, field, menu, submenu):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': 'submenu_title',
        'description': 'submenu_description',
        'price': '10.0'
    }
    response = await client.post(url, json=json)
    assert response.json().get(field) == json[field], (
        f'POST-запрос к `{DISHES_URL}` должен возвращать '
        f'корректное значение поля `{field}`'
    )


async def test_dish_post_price(client: AsyncClient, menu, submenu):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': 'dish_title',
        'description': 'dish_description',
        'price': '20.43153'
    }
    expected_price = f'{float(json["price"]):.2f}'
    response = await client.post(url, json=json)
    assert response.json().get('price') == expected_price, (
        f'POST-запрос к `{DISHES_URL}` должен возвращать корректное '
        'значение поля `price` (округленное до двух знаков после запятой)'
    )


async def test_dish_relation(client: AsyncClient, menu, submenu):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': 'dish_title',
        'description': 'dish_description',
        'price': '10'
    }
    response = await client.post(url, json=json)
    assert response.json().get('submenu_id') == str(submenu.id), (
        f'В результате POST-запроса к `{DISHES_URL}` '
        'должно создаваться блюдо с полем `submenu_id`, '
        'равным `submenu_id` из `url`'
    )


@pytest.mark.parametrize('dish_title', [None, True, 123])
async def test_dish_post_invalid_title(
    client: AsyncClient, dish_title, menu, submenu
):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': dish_title,
        'description': 'dish_description',
        'price': '123'
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'POST-запрос к `{DISHES_URL}` с невалидным полем `title` '
        'в теле запроса должен возвращать статус 422'
    )


@pytest.mark.parametrize('dish_description', [None, True, 123])
async def test_dish_post_invalid_description(
    client: AsyncClient, dish_description, menu, submenu
):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': 'dish_title',
        'description': dish_description,
        'price': '243'
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'POST-запрос к `{DISHES_URL}` с невалидным полем `description` '
        'в теле запроса должен возвращать статус 422'
    )


@pytest.mark.parametrize('dish_price', [None, True, 123, '-234', 'ds34'])
async def test_dish_post_invalid_price(
    client: AsyncClient, dish_price, menu, submenu
):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': 'dish_title',
        'description': 'dish_description',
        'price': dish_price
    }
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'POST-запрос к `{DISHES_URL}` с невалидным полем `price` '
        'в теле запроса должен возвращать статус 422'
    )


@pytest.mark.parametrize('field', ['title', 'description', 'price'])
async def test_dish_post_missing_field(
    client: AsyncClient, field, menu, submenu
):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    json = {
        'title': 'submenu_title',
        'description': 'submenu_description',
        'price': '10'
    }
    del json[field]
    response = await client.post(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'POST-запрос к `{DISHES_URL}` с отсутствующим полем `{field}` '
        'должен возвращать статус 422'
    )


async def test_dish_get_list(client: AsyncClient, menu, submenu, dish):
    url = DISHES_URL.format(menu_id=menu.id, submenu_id=submenu.id)
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'GET-запрос к `{DISHES_URL}` должен возвращать статус 200 '
        '(случай, когда в базе присутствуют блюда)'
    )
    assert response.json() != [], (
        f'GET-запрос к `{DISHES_URL}` не должен возвращать пустой список, '
        'когда в базе присутствуют блюда'
    )


async def test_dish_get_status(client: AsyncClient, menu, submenu, dish):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    response = await client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'GET-запрос к `{DISH_OBJ_URL}` должен возвращать статус 200, '
        'если блюдо с id равным `dish_id` существует в базе'
    )


async def test_dish_get_404(client: AsyncClient, menu, submenu):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=UNEXISTING_UUID
    )
    response = await client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'GET-запрос к `{DISH_OBJ_URL}` должен возвращать статус 404, '
        'если блюдо с `id` равным `dish_id` отсутствует в базе'
    )


async def test_dish_get_if_menu_404(client: AsyncClient, menu, submenu, dish):
    url = DISH_OBJ_URL.format(
        menu_id=UNEXISTING_UUID, submenu_id=submenu.id, dish_id=dish.id
    )
    response = await client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'GET-запрос к `{DISH_OBJ_URL}` должен возвращать статус 404, '
        'если меню с `id` равным `menu_id` отсутствует в базе'
    )


async def test_dish_get_if_submenu_404(
    client: AsyncClient, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=UNEXISTING_UUID, dish_id=dish.id
    )
    response = await client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'GET-запрос к `{DISH_OBJ_URL}` должен возвращать статус 404, '
        'если субменю с `id` равным `submenu_id` отсутствует в базе'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_dish_get_data(client: AsyncClient, menu, submenu, dish, field):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    response = await client.get(url)
    assert response.json().get(field) == getattr(dish, field, None), (
        f'GET-запрос к `{DISH_OBJ_URL}` должен возвращать '
        f'корректное значение поля `{field}`'
    )


async def test_dish_get_price(client: AsyncClient, menu, submenu, dish):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    expected_price = f'{float(dish.price):.2f}'
    response = await client.get(url)
    assert response.json().get('price') == expected_price, (
        f'GET-запрос к `{DISH_OBJ_URL}` должен возвращать '
        'корректное значение поля `price`'
    )


async def test_dish_get_submenu_id(client: AsyncClient, menu, submenu, dish):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    response = await client.get(url)
    assert response.json().get('submenu_id') == str(submenu.id), (
        f'GET-запрос к `{DISH_OBJ_URL}` должен возвращать корректное '
        'значение поля `submenu_id` (равное значению '
        'поля `submenu_id` из `url`)'
    )


async def test_dish_patch_status(client: AsyncClient, menu, submenu, dish):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    json = {
        'title': 'dish_title_changed',
        'description': 'dish_description_changed',
        'price': '777'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.OK, (
        f'PATCH-запрос к `{DISH_OBJ_URL}` должен возвращать статус 200, '
        'если блюдо с `dish_id` существует в базе'
    )


async def test_dish_patch_404(client: AsyncClient, menu, submenu):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=UNEXISTING_UUID
    )
    json = {
        'title': 'dish_title_changed',
        'description': 'dish_description_changed',
        'price': '777'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'PATCH-запрос к `{DISH_OBJ_URL}` должен возвращать статус 404, '
        'если блюдо с `dish_id` отсутствует в базе'
    )


async def test_dish_patch_if_menu_404(
    client: AsyncClient, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=UNEXISTING_UUID, submenu_id=submenu.id, dish_id=dish.id
    )
    json = {
        'title': 'dish_title_changed',
        'description': 'dish_description_changed',
        'price': '777'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'PATCH-запрос к `{DISH_OBJ_URL}` должен возвращать статус 404, '
        'если меню с `menu_id` отсутствует в базе'
    )


async def test_dish_patch_if_submenu_404(
    client: AsyncClient, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=UNEXISTING_UUID, dish_id=dish.id
    )
    json = {
        'title': 'dish_title_changed',
        'description': 'dish_description_changed',
        'price': '777'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'PATCH-запрос к `{DISH_OBJ_URL}` должен возвращать статус 404, '
        'если субменю с `submenu_id` отсутствует в базе'
    )


@pytest.mark.parametrize('field', ['title', 'description'])
async def test_dish_patch_data(
    client: AsyncClient, menu, submenu, dish, field
):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    json = {
        'title': 'dish_title_changed',
        'description': 'dish_description_changed',
        'price': '789'
    }
    response = await client.patch(url, json=json)
    assert response.json().get(field) == json[field], (
        f'PATCH-запрос к `{DISH_OBJ_URL}` '
        f'должен возвращать корректное значение поля `{field}`'
    )


async def test_dish_patch_price(client: AsyncClient, menu, submenu, dish):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    json = {
        'title': 'dish_title_changed',
        'description': 'dish_description_changed',
        'price': '78.854326'
    }
    expected_price = f'{float(json["price"]):.2f}'
    response = await client.patch(url, json=json)
    assert response.json().get('price') == expected_price, (
        f'PATCH-запрос к `{DISH_OBJ_URL}` '
        f'должен возвращать корректное значение поля `price`'
    )


@pytest.mark.parametrize('dish_title', [None, True, 123])
async def test_dish_patch_invalid_title(
    client: AsyncClient, dish_title, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    json = {
        'title': dish_title,
        'description': 'dish_description_changed',
        'price': '627'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'PATCH-запрос к `{DISH_OBJ_URL}` '
        'с невалидным полем `title` в теле запроса '
        'должен возвращать статус 422'
    )


@pytest.mark.parametrize('dish_description', [None, True, 123])
async def test_dish_patch_invalid_description(
    client: AsyncClient, dish_description, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    json = {
        'title': 'menu_title_changed',
        'description': dish_description,
        'price': '543'
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'PATCH-запрос к `{DISH_OBJ_URL}` '
        'с невалидным полем `description` в теле запроса '
        'должен возвращать статус 422'
    )


@pytest.mark.parametrize('dish_price', [None, True, 123, '-234', 'ds34'])
async def test_dish_patch_invalid_price(
    client: AsyncClient, dish_price, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    json = {
        'title': 'menu_title_changed',
        'description': 'dish_description',
        'price': dish_price
    }
    response = await client.patch(url, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, (
        f'PATCH-запрос к `{DISH_OBJ_URL}` '
        'с невалидным полем `price` в теле запроса '
        'должен возвращать статус 422'
    )


async def test_dish_delete_status(client: AsyncClient, menu, submenu, dish):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.OK, (
        f'DELETE-запрос к `{DISH_OBJ_URL}` '
        'должен возвращать статус 200, если блюдо с `id` '
        'равным `dish_id` существует в базе'
    )


async def test_dish_delete_404(client: AsyncClient, menu, submenu):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=UNEXISTING_UUID
    )
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'DELETE-запрос к `{DISH_OBJ_URL}` '
        'должен возвращать статус 404, если блюдо с `id` '
        'равным `dish_id` отсутствует в базе'
    )


async def test_dish_delete_if_menu_404(
    client: AsyncClient, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=UNEXISTING_UUID, submenu_id=submenu.id, dish_id=dish.id
    )
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'DELETE-запрос к `{DISH_OBJ_URL}` '
        'должен возвращать статус 404, если меню '
        'с `menu_id` отсутствует в базе'
    )


async def test_dish_delete_if_submenu_404(
    client: AsyncClient, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=UNEXISTING_UUID, dish_id=dish.id
    )
    response = await client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'DELETE-запрос к `{DISH_OBJ_URL}` '
        'должен возвращать статус 404, если субменю '
        'с `submenu_id` отсутствует в базе'
    )


async def test_dish_delete_object_deleted(
    client: AsyncClient, menu, submenu, dish
):
    url = DISH_OBJ_URL.format(
        menu_id=menu.id, submenu_id=submenu.id, dish_id=dish.id
    )
    await client.delete(url)
    async with TestingSessionLocal() as session:
        dish_exists = await session.scalar(
            select(True).where(
                (select(Dish).where(Dish.id == dish.id)).exists()
            )
        )
    assert dish_exists is None, (
        f'Убедитесь, что в результате DELETE-запроса к `{DISH_OBJ_URL}` '
        'блюдо с `id` равным `dish_id` удаляется из базы'
    )
