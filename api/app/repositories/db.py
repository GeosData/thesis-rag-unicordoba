from __future__ import annotations

import asyncpg

from app.config.settings import get_settings

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    global _pool
    settings = get_settings()
    if settings.database_url and _pool is None:
        _pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=5)


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def ping() -> bool:
    if _pool is None:
        return False
    async with _pool.acquire() as connection:
        return await connection.fetchval("SELECT 1") == 1
