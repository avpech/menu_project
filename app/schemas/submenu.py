import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, root_validator

from app.core.constants import SUBMENU_DESCR_MAX_LEN, SUBMENU_TITLE_MAX_LEN


class SubmenuBase(BaseModel):
    """Базовая схема для подменю."""
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class SubmenuCreate(SubmenuBase):
    """Схема для создания подменю."""
    title: str = Field(max_length=SUBMENU_TITLE_MAX_LEN)
    description: str = Field(max_length=SUBMENU_DESCR_MAX_LEN)


class SubmenuUpdate(SubmenuBase):
    """Схема для изменения подменю."""
    title: Optional[str] = Field(None, max_length=SUBMENU_TITLE_MAX_LEN)
    description: Optional[str] = Field(None, max_length=SUBMENU_DESCR_MAX_LEN)

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
