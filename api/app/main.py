from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import get_settings
from app.repositories import db
from app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_pool()
    yield
    await db.close_pool()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.include_router(api_router)
    return application


app = create_app()
