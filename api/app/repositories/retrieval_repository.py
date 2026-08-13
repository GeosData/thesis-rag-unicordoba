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


async def hybrid_search(
    query: str, embedding: list[float], k: int = 5, pool_size: int = 20, rrf_k: int = 60
) -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(
        """
        WITH vec AS (
            SELECT id, row_number() OVER (ORDER BY embedding <=> $2) AS rank
            FROM chunk
            ORDER BY embedding <=> $2
            LIMIT $4
        ),
        txt AS (
            SELECT id, row_number() OVER (
                ORDER BY ts_rank(tsv, websearch_to_tsquery('spanish', $1)) DESC
            ) AS rank
            FROM chunk
            WHERE tsv @@ websearch_to_tsquery('spanish', $1)
            LIMIT $4
        ),
        fused AS (
            SELECT id, sum(1.0 / ($5 + rank)) AS score
            FROM (SELECT id, rank FROM vec UNION ALL SELECT id, rank FROM txt) ranked
            GROUP BY id
        )
        SELECT t.title, t.author, t.year, t.handle, c.content,
               f.score AS score,
               1 - (c.embedding <=> $2) AS cosine
        FROM fused f
        JOIN chunk c ON c.id = f.id
        JOIN thesis t ON t.uuid = c.thesis_uuid
        ORDER BY f.score DESC
        LIMIT $3
        """,
        query,
        embedding,
        k,
        pool_size,
        rrf_k,
    )
    return [dict(row) for row in rows]
