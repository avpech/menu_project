import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator, validator

from app.core.constants import DISH_DESCR_MAX_LEN, DISH_TITLE_MAX_LEN, PRICE_SCALE
from app.schemas.validators import convert_price_to_float, field_cannot_be_null

PRICE_EXAMPLE = '20.50'


class DishBase(BaseModel):
    """Базовая схема для блюд."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class DishCreate(DishBase):
    """Схема для создания блюд."""
    title: str = Field(max_length=DISH_TITLE_MAX_LEN)
    description: str = Field(max_length=DISH_DESCR_MAX_LEN)
    price: str = Field(examples=[PRICE_EXAMPLE])

    _convert_price = validator('price', allow_reuse=True)(convert_price_to_float)


class DishUpdate(DishBase):
    """Схема для изменения блюд."""
    title: str | None = Field(None, max_length=DISH_TITLE_MAX_LEN)
    description: str | None = Field(None, max_length=DISH_DESCR_MAX_LEN)
    price: str | None = Field(None, examples=[PRICE_EXAMPLE])

    _convert_price = validator('price', allow_reuse=True)(convert_price_to_float)
    _forbid_null = validator('*', pre=True, allow_reuse=True)(field_cannot_be_null)


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
