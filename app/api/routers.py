from fastapi import APIRouter

from app.api.endpoints import dish_router, menu_router, submenu_router

PREFIX = '/menus'

main_router = APIRouter()
main_router.include_router(menu_router, prefix=PREFIX, tags=['Меню'])
main_router.include_router(submenu_router, prefix=PREFIX, tags=['Подменю'])
main_router.include_router(dish_router, prefix=PREFIX, tags=['Блюда'])
