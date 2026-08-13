from __future__ import annotations

from app.repositories.db import get_pool


async def log_query(question: str, grounded: bool, citations: int) -> None:
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO query_log (question, grounded, citations) VALUES ($1, $2, $3)",
        question,
        grounded,
        citations,
    )


async def get_stats(limit: int = 10) -> dict:
    pool = await get_pool()
    total = await pool.fetchval("SELECT count(*) FROM query_log")
    grounded = await pool.fetchval("SELECT count(*) FROM query_log WHERE grounded")
    recent = await pool.fetch(
        "SELECT question, grounded, created_at FROM query_log ORDER BY created_at DESC LIMIT $1",
        limit,
    )
    return {"total": total, "grounded": grounded, "recent": [dict(row) for row in recent]}
