from __future__ import annotations

from functools import lru_cache

from fastembed import TextEmbedding

from app.config.settings import get_settings


@lru_cache
def _model() -> TextEmbedding:
    settings = get_settings()
    if settings.fastembed_cache:
        return TextEmbedding(settings.embedding_model, cache_dir=settings.fastembed_cache)
    return TextEmbedding(settings.embedding_model)


def embed_passages(texts: list[str]) -> list[list[float]]:
    return [vector.tolist() for vector in _model().embed(texts)]


def embed_query(text: str) -> list[float]:
    return next(iter(_model().embed([text]))).tolist()
