from datetime import datetime

from pydantic import BaseModel


class RecentQuery(BaseModel):
    question: str
    grounded: bool
    created_at: datetime


class StatsResponse(BaseModel):
    total_questions: int
    grounded: int
    grounded_rate: float
    recent: list[RecentQuery]
