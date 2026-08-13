from fastapi import APIRouter

from app.schemas.stats import StatsResponse
from app.services import stats_service

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
async def stats() -> StatsResponse:
    return await stats_service.get_stats()
