import uuid

from pydantic import BaseModel, ConfigDict, Field, validator

from app.core.constants import MENU_DESCR_MAX_LEN, MENU_TITLE_MAX_LEN
from app.schemas.submenu import SubmenuNestedDishesDB
from app.schemas.validators import field_cannot_be_null

MENU_TITLE_EXAMPLE = 'Название меню'
MENU_DESCRIPTION_EXAMPLE = 'Описание меню'
MENU_TITLE_DESCR = 'Название меню'
MENU_DESCRIPTION_DESCR = 'Описание меню'


class MenuBase(BaseModel):
    """Базовая схема для меню."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class MenuCreate(MenuBase):
    """Схема для создания меню."""
    title: str = Field(
        max_length=MENU_TITLE_MAX_LEN,
        description=MENU_TITLE_DESCR,
        examples=[MENU_TITLE_EXAMPLE]
    )
    description: str = Field(
        max_length=MENU_DESCR_MAX_LEN,
        description=MENU_DESCRIPTION_DESCR,
        examples=[MENU_DESCRIPTION_EXAMPLE]
    )


class MenuUpdate(MenuBase):
    """Схема для изменения меню."""
    title: str | None = Field(
        None,
        max_length=MENU_TITLE_MAX_LEN,
        description=MENU_TITLE_DESCR,
        examples=[MENU_TITLE_EXAMPLE]
    )
    description: str | None = Field(
        None,
        max_length=MENU_DESCR_MAX_LEN,
        description=MENU_DESCRIPTION_DESCR,
        examples=[MENU_DESCRIPTION_EXAMPLE]
    )

    _forbid_null = validator('*', pre=True, allow_reuse=True)(field_cannot_be_null)


class MenuDB(BaseModel):
    """Схема для отображения данных о меню."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str = Field(
        examples=[MENU_TITLE_EXAMPLE],
        description=MENU_TITLE_DESCR
    )
    description: str = Field(
        examples=[MENU_DESCRIPTION_EXAMPLE],
        description=MENU_DESCRIPTION_DESCR
    )


class MenuWithCountDB(MenuDB):
    """
    Расширенная схема для отображения данных
    о меню с количеством подменю и блюд.
    """
    submenus_count: int = Field(description='Количество подменю в меню')
    dishes_count: int = Field(description='Количество блюд в меню')


class MenuNestedSubmenusDB(MenuDB):
    """
    Расширенная схема для отображения данных
    о меню с вложенными подменю и блюдами.
    """
    submenus: list[SubmenuNestedDishesDB] = Field(description='Список подменю в меню')
