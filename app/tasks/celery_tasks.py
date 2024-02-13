import asyncio

from celery import Celery

from app.core.config import broker_url
from app.core.db import AsyncSessionLocal
from app.crud.dish import CRUDDish
from app.crud.menu import CRUDMenu
from app.crud.submenu import CRUDSubmenu
from app.tasks.utils import SyncDatabaseData, get_table_data

celery_app = Celery('hello', broker=broker_url)


async def update_db() -> None:
    table_data = get_table_data()
    async with AsyncSessionLocal() as session:

        menu_crud = CRUDMenu()
        menu_crud.session = session
        submenu_crud = CRUDSubmenu()
        submenu_crud.session = session
        dish_crud = CRUDDish()
        dish_crud.session = session
        sync = SyncDatabaseData(menu_crud, submenu_crud, dish_crud)

        db_data = await menu_crud.get_all()

        await sync.delete_inconsistent_db_data(table_data, db_data)
        await sync.update_db_data(table_data, db_data)


@celery_app.task
def sync_table_db() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_db())


celery_app.conf.beat_schedule = {
    'run-every-15-seconds': {
        'task': 'app.tasks.celery_tasks.sync_table_db',
        'schedule': 15.0
    }
}
