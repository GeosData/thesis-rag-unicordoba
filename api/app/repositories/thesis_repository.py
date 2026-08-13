from __future__ import annotations

from app.repositories.db import get_pool


async def upsert_thesis(item: dict) -> None:
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO thesis (uuid, title, author, advisor, year, type, keywords, abstract, handle)
        VALUES ($1::uuid, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (uuid) DO UPDATE SET
            title = EXCLUDED.title,
            author = EXCLUDED.author,
            advisor = EXCLUDED.advisor,
            year = EXCLUDED.year,
            type = EXCLUDED.type,
            keywords = EXCLUDED.keywords,
            abstract = EXCLUDED.abstract,
            handle = EXCLUDED.handle
        """,
        item["uuid"],
        item.get("title"),
        item.get("author"),
        item.get("advisor"),
        item.get("year"),
        item.get("type"),
        item.get("keywords"),
        item.get("abstract"),
        item.get("handle"),
    )


async def replace_chunks(
    thesis_uuid: str, chunks: list[str], embeddings: list[list[float]]
) -> None:
    pool = await get_pool()
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                "DELETE FROM chunk WHERE thesis_uuid = $1::uuid", thesis_uuid
            )
            for order, (content, embedding) in enumerate(zip(chunks, embeddings)):
                await connection.execute(
                    "INSERT INTO chunk (thesis_uuid, ord, content, embedding) "
                    "VALUES ($1::uuid, $2, $3, $4)",
                    thesis_uuid,
                    order,
                    content,
                    embedding,
                )
