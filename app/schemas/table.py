from pydantic import BaseModel, Field, field_validator


class DishTable(BaseModel):
    """Схема для табличных данных о блюде."""
    title: str
    description: str
    price: float
    discount: str | float | None

    @field_validator('discount', mode='before')
    @classmethod
    def check_discount(cls, value: str | float | None) -> str | float | None:
        if not value:
            return value
        if isinstance(value, str):
            value = value.replace(',', '.').replace('%', '')
            value = float(value) / 100
        if value < 0:
            raise ValueError('Скидка не может иметь отрицательное значение')
        if value > 1:
            raise ValueError('Скидка не может быть больше 100%')
        return value

    @field_validator('price')
    @classmethod
    def price_not_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError('Цена не может иметь отрицательное значение')
        return value


class SubmenuTable(BaseModel):
    """Схема для табличных данных о подменю."""
    title: str
    description: str
    dishes: list[DishTable] = Field(default_factory=list)


class MenuTable(BaseModel):
    """Схема для табличных данных о меню."""
    title: str
    description: str
    submenus: list[SubmenuTable] = Field(default_factory=list)
