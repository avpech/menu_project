from fastapi import APIRouter

from app.api.endpoints import dish_router, menu_router, submenu_router

PREFIX = '/menus'

main_router = APIRouter()
main_router.include_router(menu_router, prefix=PREFIX, tags=['Menus'])
main_router.include_router(submenu_router, prefix=PREFIX, tags=['Submenus'])
main_router.include_router(dish_router, prefix=PREFIX, tags=['Dishes'])
