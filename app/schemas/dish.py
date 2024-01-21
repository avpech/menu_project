import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, root_validator, validator

from app.core.constants import (DISH_DESCR_MAX_LEN, DISH_TITLE_MAX_LEN,
                                PRICE_SCALE)


class DishBase(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class DishCreate(DishBase):
    title: str = Field(max_length=DISH_TITLE_MAX_LEN)
    description: str = Field(max_length=DISH_DESCR_MAX_LEN)
    price: str

    @validator('price')
    def convert_price_to_float(cls, value: str):
        price = float(value)
        if price < 0:
            raise ValueError('price не может иметь отрицательное значение')
        return price


class DishUpdate(DishCreate):
    title: Optional[str] = Field(None, max_length=DISH_TITLE_MAX_LEN)
    description: Optional[str] = Field(None, max_length=DISH_DESCR_MAX_LEN)
    price: Optional[str]

    @root_validator(pre=True)
    def field_cannot_be_null(
        cls,
        values: dict[str, Optional[str]]
    ) -> dict[str, Optional[str]]:
        """Валидация на недопустимость передачи полю значения null."""

        for field in ('title', 'description', 'price'):
            if field in values and values[field] is None:
                raise ValueError(f'Значение поля {field} не может быть null.')
        return values


class DishDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    price: str
    submenu_id: uuid.UUID

    @validator('price', pre=True)
    def convert_price_to_str(cls, value: float):
        return f'{value:.{PRICE_SCALE}f}'
