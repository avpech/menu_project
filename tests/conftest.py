import asyncio
import os

import pytest
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import get_async_session
from app.main import app
from app.models import Base, Dish, Menu, Submenu

load_dotenv()

UNEXISTING_UUID = '00000000-0000-0000-0000-000000000000'
MENUS_URL = '/api/v1/menus/'
MENU_OBJ_URL = '/api/v1/menus/{menu_id}'
SUBMENUS_URL = '/api/v1/menus/{menu_id}/submenus'
SUBMENU_OBJ_URL = '/api/v1/menus/{menu_id}/submenus/{submenu_id}'
DISHES_URL = '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes'
DISH_OBJ_URL = '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'

test_db_url = (
    f'postgresql+asyncpg://{os.environ["DB_USER"]}:'
    f'{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:'
    f'{os.environ["DB_PORT"]}/{os.environ["TEST_DB_NAME"]}'
)

engine = create_async_engine(test_db_url)


TestingSessionLocal = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=engine,
)


async def override_get_async_session():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture()
async def menu():
    """Фикстура меню."""
    async with TestingSessionLocal() as session:
        menu = Menu(title='menu_title_fixture', description='menu_description')
        session.add(menu)
        await session.commit()
        await session.refresh(menu)
    return menu


@pytest.fixture()
async def submenu(menu):
    """Фикстура субменю."""
    async with TestingSessionLocal() as session:
        submenu = Submenu(
            title='submenu_title',
            description='submenu_description',
            menu_id=menu.id
        )
        session.add(submenu)
        await session.commit()
        await session.refresh(submenu)
    return submenu


@pytest.fixture()
async def dish(submenu):
    """Фикстура блюда."""
    async with TestingSessionLocal() as session:
        dish = Dish(
            title='dish_title',
            description='dish_description',
            price=10.0,
            submenu_id=submenu.id
        )
        session.add(dish)
        await session.commit()
        await session.refresh(dish)
    return dish


@pytest.fixture()
async def dish_another(submenu):
    """Альтернативная фикстура блюда."""
    async with TestingSessionLocal() as session:
        dish = Dish(
            title='dish_title',
            description='dish_description',
            price=10.0,
            submenu_id=submenu.id
        )
        session.add(dish)
        await session.commit()
        await session.refresh(dish)
    return dish
