import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator, validator

from app.core.constants import DISH_DESCR_MAX_LEN, DISH_TITLE_MAX_LEN, PRICE_SCALE
from app.schemas.validators import convert_price_to_float, field_cannot_be_null

PRICE_EXAMPLE = '20.50'
DISH_TITLE_EXAMPLE = 'Название блюда'
DISH_DESCRIPTION_EXAMPLE = 'Описание блюда'
PRICE_DESCR = 'Цена блюда. Должно быть неотрицательное значение'
DISH_TITLE_DESCR = 'Название блюда'
DISH_DESCRIPTION_DESCR = 'Описание блюда'


class DishBase(BaseModel):
    """Базовая схема для блюд."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class DishCreate(DishBase):
    """Схема для создания блюд."""
    title: str = Field(
        max_length=DISH_TITLE_MAX_LEN,
        description=DISH_TITLE_DESCR,
        examples=[DISH_TITLE_EXAMPLE]
    )
    description: str = Field(
        max_length=DISH_DESCR_MAX_LEN,
        description=DISH_DESCRIPTION_DESCR,
        examples=[DISH_DESCRIPTION_EXAMPLE]
    )
    price: str = Field(
        description=PRICE_DESCR,
        examples=[PRICE_EXAMPLE]
    )

    _convert_price = validator('price', allow_reuse=True)(convert_price_to_float)


class DishUpdate(DishBase):
    """Схема для изменения блюд."""
    title: str | None = Field(
        None,
        max_length=DISH_TITLE_MAX_LEN,
        description=DISH_TITLE_DESCR,
        examples=[DISH_TITLE_EXAMPLE]
    )
    description: str | None = Field(
        None,
        max_length=DISH_DESCR_MAX_LEN,
        description=DISH_DESCRIPTION_DESCR,
        examples=[DISH_DESCRIPTION_EXAMPLE]
    )
    price: str | None = Field(
        None,
        description=PRICE_DESCR,
        examples=[PRICE_EXAMPLE]
    )

    _convert_price = validator('price', allow_reuse=True)(convert_price_to_float)
    _forbid_null = validator('*', pre=True, allow_reuse=True)(field_cannot_be_null)


class DishDB(BaseModel):
    """Схема для отображения данных о блюдах."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str = Field(
        description=DISH_TITLE_DESCR,
        examples=[DISH_TITLE_EXAMPLE]
    )
    description: str = Field(
        description=DISH_DESCRIPTION_DESCR,
        examples=[DISH_DESCRIPTION_EXAMPLE]
    )
    price: str = Field(
        description=PRICE_DESCR,
        examples=[PRICE_EXAMPLE]
    )
    submenu_id: uuid.UUID = Field(description='id связанного подменю')

    @field_validator('price', mode='before')
    @classmethod
    def convert_price_to_str(cls, value: float) -> str:
        return f'{value:.{PRICE_SCALE}f}'


class DishDiscountDB(DishDB):
    discount: str = Field(description='Размер скидки', examples=['0%'])
