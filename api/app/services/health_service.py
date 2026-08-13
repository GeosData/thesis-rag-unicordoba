from app.config.settings import get_settings
from app.repositories import db
from app.schemas.health import HealthResponse


async def check_health() -> HealthResponse:
    settings = get_settings()
    if settings.database_url is None:
        database = "not_configured"
    else:
        database = "up" if await db.ping() else "down"
    status = "ok" if database in ("up", "not_configured") else "degraded"
    return HealthResponse(
        status=status,
        service=settings.app_name,
        environment=settings.environment,
        database=database,
    )
