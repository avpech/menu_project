import uuid
from http import HTTPStatus
from typing import Generic, TypeVar

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
AnyType = TypeVar('AnyType')


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс для CRUD-операций."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_async_session)
    ) -> None:
        self.model: type[ModelType]
        self.session = session

    def _exists_or_404(
        self,
        obj: AnyType | None,
        detail: str = 'not found'
    ) -> AnyType:
        """
        Проверка существования объекта.

        Вызывает HTTPException со статусом 404, если объект `None`.
        """
        if obj is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=detail
            )
        return obj

    async def get(
        self,
        obj_id: uuid.UUID
    ) -> ModelType | None:
        """Получение объекта по id."""
        return await self.session.get(self.model, obj_id)

    async def get_or_404(
        self,
        obj_id: uuid.UUID
    ) -> ModelType:
        """
        Получение объекта по id.

        При отсутствии объекта вызывает HTTPException со статусом 404.
        """
        obj = await self.get(obj_id)
        return self._exists_or_404(obj)

    async def get_multi(self) -> list[ModelType]:
        """Получение всех объектов."""
        db_objs = await self.session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        **kwargs
    ) -> ModelType:
        """
        Создание объекта.

        В `**kwargs` передаются поля, отсутствующие в Pydantic-схеме.
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, **kwargs)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Частичное обновление объекта."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj: ModelType
    ) -> ModelType:
        """Удаление объекта."""
        await self.session.delete(db_obj)
        await self.session.commit()
        return db_obj
