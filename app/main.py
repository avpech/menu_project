from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.core.redis_cache import cache

app = FastAPI(title=settings.app_title, description=settings.description)

app.include_router(main_router, prefix='/api/v1')

app.add_event_handler('startup', cache.clean)
app.add_event_handler('shutdown', cache.disconnect)
