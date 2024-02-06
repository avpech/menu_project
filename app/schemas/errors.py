from pydantic import BaseModel, Field


class URLDoesNotExistError(BaseModel):
    """URL не найден."""
    detail: str = Field(examples=['url not found'])


class MenuNotFoundError(BaseModel):
    """Меню не найдено."""
    detail: str = Field(examples=['menu not found'])


class SubmenuNotFoundError(BaseModel):
    """Субменю не найдено."""
    detail: str = Field(examples=['submenu not found'])


class DishNotFoundError(BaseModel):
    """Блюдо не найдено."""
    detail: str = Field(examples=['dish not found'])
