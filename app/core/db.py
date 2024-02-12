from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import db_url

engine = create_async_engine(db_url)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """Асинхронный генератор сессий."""
    async with AsyncSessionLocal() as session:
        yield session
