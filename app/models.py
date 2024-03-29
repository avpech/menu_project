import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from app.core.constants import (
    DISH_DESCR_MAX_LEN,
    DISH_TITLE_MAX_LEN,
    MENU_DESCR_MAX_LEN,
    MENU_TITLE_MAX_LEN,
    SUBMENU_DESCR_MAX_LEN,
    SUBMENU_TITLE_MAX_LEN,
)


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )


class Menu(Base):
    """Модель для меню."""
    title: Mapped[str] = mapped_column(
        String(MENU_TITLE_MAX_LEN),
        unique=True
    )
    description: Mapped[str] = mapped_column(String(MENU_DESCR_MAX_LEN))
    submenus: Mapped[list['Submenu']] = relationship(
        cascade='all, delete-orphan'
    )


class Submenu(Base):
    """Модель для подменю."""
    title: Mapped[str] = mapped_column(
        String(SUBMENU_TITLE_MAX_LEN),
        unique=True
    )
    description: Mapped[str] = mapped_column(
        String(SUBMENU_DESCR_MAX_LEN)
    )
    menu_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('menu.id'))
    menu: Mapped['Menu'] = relationship(back_populates='submenus')
    dishes: Mapped[list['Dish']] = relationship(cascade='all, delete-orphan')


class Dish(Base):
    """Модель для блюд."""
    title: Mapped[str] = mapped_column(
        String(DISH_TITLE_MAX_LEN),
        unique=True
    )
    description: Mapped[str] = mapped_column(String(DISH_DESCR_MAX_LEN))
    price: Mapped[float] = mapped_column()
    submenu_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('submenu.id'))
    submenu: Mapped['Submenu'] = relationship(back_populates='dishes')
    __table_args__ = (
        CheckConstraint('price >= 0', name='price_not_negative'),
    )
