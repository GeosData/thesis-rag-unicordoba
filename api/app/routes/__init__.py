from fastapi import APIRouter

from app.routes import ask, health, stats

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ask.router)
api_router.include_router(stats.router)
