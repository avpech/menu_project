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


class DishCacheDict(TypedDict):
    """Словарь для кэшированных данных о блюде."""
    id: str
    title: str
    description: str
    price: float
    submenu_id: str
