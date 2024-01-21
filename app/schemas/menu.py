import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, root_validator

from app.core.constants import MENU_DESCR_MAX_LEN, MENU_TITLE_MAX_LEN


class MenuBase(BaseModel):
    """Базовая схема для меню."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class MenuCreate(MenuBase):
    """Схема для создания меню."""
    title: str = Field(max_length=MENU_TITLE_MAX_LEN)
    description: str = Field(max_length=MENU_DESCR_MAX_LEN)


class MenuUpdate(MenuBase):
    """Схема для изменения меню."""
    title: Optional[str] = Field(None, max_length=MENU_TITLE_MAX_LEN)
    description: Optional[str] = Field(None, max_length=MENU_DESCR_MAX_LEN)

    @root_validator(pre=True)
    def field_cannot_be_null(
        cls,
        values: dict[str, Optional[str]]
    ) -> dict[str, Optional[str]]:
        """Валидация на недопустимость передачи полю значения null."""

        for field in ('title', 'description'):
            if field in values and values[field] is None:
                raise ValueError(f'Значение поля {field} не может быть null.')
        return values


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
