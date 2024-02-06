import uuid

from pydantic import BaseModel, ConfigDict, Field, validator

from app.core.constants import SUBMENU_DESCR_MAX_LEN, SUBMENU_TITLE_MAX_LEN
from app.schemas.validators import field_cannot_be_null

SUBMENU_TITLE_EXAMPLE = 'Название подменю'
SUBMENU_DESCRIPTION_EXAMPLE = 'Описание подменю'
SUBMENU_TITLE_DESCR = 'Название подменю'
SUBMENU_DESCRIPTION_DESCR = 'Описание подменю'


class SubmenuBase(BaseModel):
    """Базовая схема для подменю."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class SubmenuCreate(SubmenuBase):
    """Схема для создания подменю."""
    title: str = Field(
        max_length=SUBMENU_TITLE_MAX_LEN,
        description=SUBMENU_TITLE_DESCR,
        examples=[SUBMENU_TITLE_EXAMPLE]
    )
    description: str = Field(
        max_length=SUBMENU_DESCR_MAX_LEN,
        description=SUBMENU_DESCRIPTION_DESCR,
        examples=[SUBMENU_DESCRIPTION_EXAMPLE]
    )


class SubmenuUpdate(SubmenuBase):
    """Схема для изменения подменю."""
    title: str | None = Field(
        None,
        max_length=SUBMENU_TITLE_MAX_LEN,
        description=SUBMENU_TITLE_DESCR,
        examples=[SUBMENU_TITLE_EXAMPLE]
    )
    description: str | None = Field(
        None,
        max_length=SUBMENU_DESCR_MAX_LEN,
        description=SUBMENU_DESCRIPTION_DESCR,
        examples=[SUBMENU_DESCRIPTION_EXAMPLE]
    )

    _forbid_null = validator('*', pre=True, allow_reuse=True)(field_cannot_be_null)


class SubmenuDB(BaseModel):
    """Схема для отображения данных о подменю."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str = Field(
        description=SUBMENU_TITLE_DESCR,
        examples=[SUBMENU_TITLE_EXAMPLE]
    )
    description: str = Field(
        description=SUBMENU_DESCRIPTION_DESCR,
        examples=[SUBMENU_DESCRIPTION_EXAMPLE]
    )
    menu_id: uuid.UUID = Field(description='id связанного меню')


class SubmenuWithCountDB(SubmenuDB):
    """Расширенная схема для отображения данных о подменю."""
    dishes_count: int = Field(description='Количество блюд в подменю')
