from __future__ import annotations

from app.repositories.db import get_pool


async def search(embedding: list[float], k: int = 5) -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT t.title, t.author, t.year, t.handle, c.content,
               1 - (c.embedding <=> $1) AS score
        FROM chunk c
        JOIN thesis t ON t.uuid = c.thesis_uuid
        ORDER BY c.embedding <=> $1
        LIMIT $2
        """,
        embedding,
        k,
    )
    return [dict(row) for row in rows]
