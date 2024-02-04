GET_ALL_MENUS = 'get_all_menus'
CREATE_MENU = 'create_menu'
GET_MENU = 'get_menu'
UPDATE_MENU = 'update_menu'
DELETE_MENU = 'delete_menu'

GET_ALL_SUBMENUS = 'get_all_submenus'
CREATE_SUBMENU = 'create_submenu'
GET_SUBMENU = 'get_submenu'
UPDATE_SUBMENU = 'update_submenu'
DELETE_SUBMENU = 'delete_submenu'

GET_ALL_DISHES = 'get_all_dishes'
CREATE_DISH = 'create_dish'
GET_DISH = 'get_dish'
UPDATE_DISH = 'update_dish'
DELETE_DISH = 'delete_dish'

UNEXISTING_UUID = '00000000-0000-0000-0000-000000000000'

MENUS_URL = '/api/v1/menus/'
MENU_OBJ_URL = '/api/v1/menus/{menu_id}'
SUBMENUS_URL = '/api/v1/menus/{menu_id}/submenus'
SUBMENU_OBJ_URL = '/api/v1/menus/{menu_id}/submenus/{submenu_id}'
DISHES_URL = '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes'
DISH_OBJ_URL = '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
