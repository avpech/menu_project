import uuid
from typing import TypedDict


class MenuAnnotatedDict(TypedDict):
    """Словарь для данных о меню с аннотациями."""
    id: uuid.UUID
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class MenuCachedDict(TypedDict):
    """Словарь для кэшированных данных о меню."""
    id: str
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class SubmenuAnnotatedDict(TypedDict):
    """Словарь для данных о подменю с аннотациями."""
    id: uuid.UUID
    title: str
    description: str
    menu_id: uuid.UUID
    dishes_count: int


class SubmenuCachedDict(TypedDict):
    """Словарь для кэшированных данных о подменю."""
    id: str
    title: str
    description: str
    menu_id: str
    dishes_count: int


class DishDiscountDict(TypedDict):
    """Словарь для данных о блюде со скидкой."""
    id: uuid.UUID
    title: str
    description: str
    price: str
    discount: str
    submenu_id: uuid.UUID


class DishCachedDiscountDict(TypedDict):
    """Словарь для кэшированных данных о блюде со скидкой."""
    id: str
    title: str
    description: str
    price: float
    discount: str
    submenu_id: str


class DishDict(TypedDict):
    """Словарь для данных о блюде."""
    id: uuid.UUID
    title: str
    description: str
    price: float
    submenu_id: uuid.UUID


class SubmenuNesteDishesDict(TypedDict):
    """Словарь для данных о подменю с вложенными блюдами."""
    id: uuid.UUID
    title: str
    description: str
    menu_id: uuid.UUID
    dishes: list[DishDiscountDict]


class SubmenuCachedNesteDishesDict(TypedDict):
    """Словарь для кжшированных данных о подменю с вложенными блюдами."""
    id: str
    title: str
    description: str
    menu_id: str
    dishes: list[DishCachedDiscountDict]


class MenuNestedSubmenusDict(TypedDict):
    """Словарь для данных о меню с вложенными подменю."""
    id: uuid.UUID
    title: str
    description: str
    submenus: list[SubmenuNesteDishesDict]


class MenuCachedNestedSubmenusDict(TypedDict):
    """Словарь для кэшированных данных о меню с вложенными подменю."""
    id: str
    title: str
    description: str
    submenus: list[SubmenuCachedNesteDishesDict]
