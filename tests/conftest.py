import asyncio
import os
from typing import AsyncIterator, Iterator

import pytest
import redis.asyncio as redis
from dotenv import load_dotenv
from httpx import AsyncClient
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.core.db import get_async_session
from app.main import app
from app.models import Base, Dish, Menu, Submenu

load_dotenv()


test_db_url = (
    f'postgresql+asyncpg://{os.environ["DB_USER"]}:'
    f'{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:'
    f'{os.environ["DB_PORT"]}/{os.environ["TEST_DB_NAME"]}'
)

engine = create_async_engine(test_db_url)


TestingSessionLocal = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=engine,
)


async def override_get_async_session() -> AsyncIterator[AsyncSession]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope='session')
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope='session')
async def redis_client() -> AsyncIterator[Redis]:
    client: Redis = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379))
    )
    await client.flushdb()
    yield client
    await client.close()


@pytest.fixture(autouse=True, scope='function')
async def clear_cache(redis_client: Redis):
    await redis_client.flushdb()


@pytest.fixture(autouse=True, scope='session')
async def init_db() -> AsyncIterator[AsyncEngine]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True, scope='function')
async def clear_db(init_db: AsyncEngine) -> AsyncIterator[AsyncSession]:
    internal_session = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=init_db,
        class_=AsyncSession,
    )
    async with internal_session() as session:
        await session.begin()
        yield session
        await session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f'TRUNCATE {table.name} CASCADE'))
            await session.commit()


@pytest.fixture(scope='session')
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest.fixture()
async def menu() -> Menu:
    """Фикстура меню."""
    async with TestingSessionLocal() as session:
        menu = Menu(title='menu_title_fixture', description='menu_description')
        session.add(menu)
        await session.commit()
        await session.refresh(menu)
    return menu


@pytest.fixture()
async def submenu(menu: Menu) -> Submenu:
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
async def dish(submenu: Submenu) -> Dish:
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
async def dish_another(submenu: Submenu) -> Dish:
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
