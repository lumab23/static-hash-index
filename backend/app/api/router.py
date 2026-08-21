from fastapi import APIRouter

from app.api.routes.data import router as data_router
from app.api.routes.health import router as health_router
from app.api.routes.index_search import router as index_search_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(data_router)
api_router.include_router(index_search_router)
