MENU_TITLE_MAX_LEN = 50
MENU_DESCR_MAX_LEN = 200
SUBMENU_TITLE_MAX_LEN = 50
SUBMENU_DESCR_MAX_LEN = 200
DISH_TITLE_MAX_LEN = 50
DISH_DESCR_MAX_LEN = 1000
PRICE_SCALE = 2

MENU_ID_DESCR = 'Идентификатор меню'
SUBMENU_ID_DESCR = 'Идентификатор подменю'
DISH_ID_DESCR = 'Идентификатор блюда'

GET_LIST_TAG = 'GET-запросы (получение списка объектов)'
POST_TAG = 'POST-запросы (создание объекта)'
GET_TAG = 'GET-запросы (получение определенного объекта)'
PATCH_TAG = 'PATCH-запросы (обновление объекта)'
DELETE_TAG = 'DELETE-запросы (удаление объекта)'
MENU_TAG = 'Меню'
SUBMENU_TAG = 'Подменю'
DISH_TAG = 'Блюда'

TAGS_METADATA = [
    {
        'name': f'{MENU_TAG}',
        'description': 'Взаимодействие с меню.',
    },
    {
        'name': f'{SUBMENU_TAG}',
        'description': 'Взаимодействие с подменю.',
    },
    {
        'name': f'{DISH_TAG}',
        'description': 'Взаимодействие с блюдами.',
    },
    {
        'name': f'{GET_LIST_TAG}'
    },
    {
        'name': f'{GET_TAG}'
    },
    {
        'name': f'{POST_TAG}'
    },
    {
        'name': f'{PATCH_TAG}'
    },
    {
        'name': f'{DELETE_TAG}'
    },
]
