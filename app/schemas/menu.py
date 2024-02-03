import uuid

from pydantic import BaseModel, ConfigDict, Field, validator

from app.core.constants import MENU_DESCR_MAX_LEN, MENU_TITLE_MAX_LEN
from app.schemas.validators import field_cannot_be_null


class MenuBase(BaseModel):
    """Базовая схема для меню."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class MenuCreate(MenuBase):
    """Схема для создания меню."""
    title: str = Field(max_length=MENU_TITLE_MAX_LEN)
    description: str = Field(max_length=MENU_DESCR_MAX_LEN)


class MenuUpdate(MenuBase):
    """Схема для изменения меню."""
    title: str | None = Field(None, max_length=MENU_TITLE_MAX_LEN)
    description: str | None = Field(None, max_length=MENU_DESCR_MAX_LEN)

    _forbid_null = validator('*', pre=True, allow_reuse=True)(field_cannot_be_null)


class MenuDB(BaseModel):
    """Схема для отображения данных о меню."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str


class MenuWithCountDB(MenuDB):
    """Расширенная схема для отображения данных о меню."""
    dishes_count: int
    submenus_count: int
