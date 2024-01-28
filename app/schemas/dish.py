import uuid
from typing import Optional

from pydantic import (BaseModel, ConfigDict, Field, field_validator,
                      model_validator)

from app.core.constants import (DISH_DESCR_MAX_LEN, DISH_TITLE_MAX_LEN,
                                PRICE_SCALE)

PRICE_EXAMPLE = '20.50'


class DishBase(BaseModel):
    """Базовая схема для блюд."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class DishCreate(DishBase):
    """Схема для создания блюд."""
    title: str = Field(max_length=DISH_TITLE_MAX_LEN)
    description: str = Field(max_length=DISH_DESCR_MAX_LEN)
    price: str = Field(examples=[PRICE_EXAMPLE])

    @field_validator('price')
    @classmethod
    def convert_price_to_float_and_check_not_negative(cls, value: str):
        price = float(value)
        if price < 0:
            raise ValueError('price не может иметь отрицательное значение')
        return price


class DishUpdate(DishCreate):
    """Схема для изменения блюд."""
    title: Optional[str] = Field(None, max_length=DISH_TITLE_MAX_LEN)
    description: Optional[str] = Field(None, max_length=DISH_DESCR_MAX_LEN)
    price: Optional[str] = Field(None, examples=[PRICE_EXAMPLE])

    @model_validator(mode='before')
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
    """Схема для отображения данных о блюдах."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    price: str = Field(examples=[PRICE_EXAMPLE])
    submenu_id: uuid.UUID

    @field_validator('price', mode='before')
    def convert_price_to_str(cls, value: float):
        return f'{value:.{PRICE_SCALE}f}'
