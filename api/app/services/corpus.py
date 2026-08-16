from __future__ import annotations

import json
from pathlib import Path


def load_corpus(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_document(item: dict) -> str:
    parts = [item.get("title"), item.get("keywords"), item.get("abstract")]
    return "\n".join(part.strip() for part in parts if part and part.strip())


def build_chunks(item: dict, fulltext: str | None) -> list[str]:
    metadata = build_document(item)
    chunks: list[str] = [metadata] if metadata else []
    if fulltext:
        chunks.extend(chunk_text(fulltext))
    return chunks


def chunk_text(text: str, size: int = 1000, overlap: int = 150) -> list[str]:
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return chunks
