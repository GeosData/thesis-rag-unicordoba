from __future__ import annotations

from app.repositories import query_log_repository
from app.schemas.stats import RecentQuery, StatsResponse


async def get_stats() -> StatsResponse:
    data = await query_log_repository.get_stats()
    total = data["total"] or 0
    grounded = data["grounded"] or 0
    return StatsResponse(
        total_questions=total,
        grounded=grounded,
        grounded_rate=round(grounded / total, 3) if total else 0.0,
        recent=[RecentQuery(**row) for row in data["recent"]],
    )
