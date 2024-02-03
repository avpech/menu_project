import uuid

from pydantic import BaseModel, ConfigDict, Field, validator

from app.core.constants import SUBMENU_DESCR_MAX_LEN, SUBMENU_TITLE_MAX_LEN
from app.schemas.validators import field_cannot_be_null


class SubmenuBase(BaseModel):
    """Базовая схема для подменю."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class SubmenuCreate(SubmenuBase):
    """Схема для создания подменю."""
    title: str = Field(max_length=SUBMENU_TITLE_MAX_LEN)
    description: str = Field(max_length=SUBMENU_DESCR_MAX_LEN)


class SubmenuUpdate(SubmenuBase):
    """Схема для изменения подменю."""
    title: str | None = Field(None, max_length=SUBMENU_TITLE_MAX_LEN)
    description: str | None = Field(None, max_length=SUBMENU_DESCR_MAX_LEN)

    _forbid_null = validator('*', pre=True, allow_reuse=True)(field_cannot_be_null)


class SubmenuDB(BaseModel):
    """Схема для отображения данных о подменю."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    menu_id: uuid.UUID


class SubmenuWithCountDB(SubmenuDB):
    """Расширенная схема для отображения данных о подменю."""
    dishes_count: int
