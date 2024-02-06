from fastapi import APIRouter

from app.api.endpoints import dish_router, menu_router, submenu_router
from app.core.constants import DISH_TAG, MENU_TAG, SUBMENU_TAG

PREFIX = '/menus'

main_router = APIRouter()
main_router.include_router(menu_router, prefix=PREFIX, tags=[MENU_TAG])
main_router.include_router(submenu_router, prefix=PREFIX, tags=[SUBMENU_TAG])
main_router.include_router(dish_router, prefix=PREFIX, tags=[DISH_TAG])
