from __future__ import annotations

import asyncpg
from pgvector.asyncpg import register_vector

from app.config.settings import get_settings

_pool: asyncpg.Pool | None = None


async def _setup_connection(connection: asyncpg.Connection) -> None:
    await register_vector(connection)


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        settings = get_settings()
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is not configured")
        _pool = await asyncpg.create_pool(
            settings.database_url, min_size=1, max_size=5, init=_setup_connection
        )
    return _pool


async def init_pool() -> None:
    if get_settings().database_url:
        await get_pool()


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
