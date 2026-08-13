from app.schemas.health import HealthResponse
from app.services import health_service


async def get_health() -> HealthResponse:
    return await health_service.check_health()
