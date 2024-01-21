import uuid
from http import HTTPStatus
from typing import Generic, Optional, Type, TypeVar

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс для CRUD-операций."""

    def __init__(
        self,
        model: Type[ModelType]
    ) -> None:
        self.model = model

    async def get(
        self,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """Получение объекта по id."""
        return await session.get(self.model, obj_id)

    async def get_or_404(
        self,
        obj_id: uuid.UUID,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        """
        Получение объекта по id.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get(obj_id, session)
        if obj is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f'{self.model.__tablename__} not found'
            )
        return obj

    async def get_multi(
        self,
        session: AsyncSession
    ) -> list[ModelType]:
        """Получение всех объектов."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession
    ) -> ModelType:
        """Создание объекта."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
    ) -> ModelType:
        """Частичное обновление объекта."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj: ModelType,
        session: AsyncSession,
    ) -> ModelType:
        """Удаление объекта."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj
