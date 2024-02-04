import uuid
from typing import TypedDict


class MenuAnnotatedDict(TypedDict):
    id: uuid.UUID
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class MenuCachedDict(TypedDict):
    id: str
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class SubmenuAnnotatedDict(TypedDict):
    id: uuid.UUID
    title: str
    description: str
    menu_id: uuid.UUID
    dishes_count: int


class SubmenuCachedDict(TypedDict):
    id: str
    title: str
    description: str
    menu_id: str
    dishes_count: int


class DishCacheDict(TypedDict):
    id: str
    title: str
    description: str
    price: float
    submenu_id: str
