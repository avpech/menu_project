import asyncio

from celery import Celery

from app.core.config import broker_url
from app.core.db import AsyncSessionLocal
from app.crud import menu_crud
from app.tasks.utils import delete_inconsistent_db_data, get_table_data, update_db_data

celery_app = Celery('hello', broker=broker_url)


async def update_db() -> None:
    table_data = get_table_data()
    async with AsyncSessionLocal() as session:
        db_data = await menu_crud.get_all(session)
        await delete_inconsistent_db_data(table_data, db_data, session)
        await update_db_data(table_data, db_data, session)


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
