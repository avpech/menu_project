from pydantic import BaseModel, Field


class URLDoesNotExistError(BaseModel):
    """Схема для документации (url не найден)."""
    detail: str = Field(examples=['url not found'])


class MenuNotFoundError(BaseModel):
    """Схема для документации (меню не найдено)."""
    detail: str = Field(examples=['menu not found'])


class SubmenuNotFoundError(BaseModel):
    """Схема для документации (субменю не найдено)."""
    detail: str = Field(examples=['submenu not found'])


class DishNotFoundError(BaseModel):
    """Схема для документации (блюдо не найдено)."""
    detail: str = Field(examples=['dish not found'])
