from __future__ import annotations

from functools import lru_cache

from fastembed import TextEmbedding

from app.config.settings import get_settings


@lru_cache
def _model() -> TextEmbedding:
    return TextEmbedding(get_settings().embedding_model)


def embed_passages(texts: list[str]) -> list[list[float]]:
    return [vector.tolist() for vector in _model().embed(texts)]


def embed_query(text: str) -> list[float]:
    return next(iter(_model().embed([text]))).tolist()
