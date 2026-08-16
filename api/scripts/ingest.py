from __future__ import annotations

import asyncio

from app.config.settings import get_settings
from app.repositories import db, thesis_repository
from app.services import corpus, embeddings, fulltext


async def main() -> None:
    settings = get_settings()
    items = corpus.load_corpus(settings.corpus_path)
    print(f"corpus: {len(items)} thesis")
    await db.get_pool()
    indexed = 0
    metadata_only = 0
    total_chunks = 0
    for position, item in enumerate(items, start=1):
        body = fulltext.fetch_fulltext(item["uuid"])
        if body is None:
            metadata_only += 1
        chunks = corpus.build_chunks(item, body)
        if not chunks:
            continue
        vectors = embeddings.embed_passages(chunks)
        await thesis_repository.upsert_thesis(item)
        await thesis_repository.replace_chunks(item["uuid"], chunks, vectors)
        indexed += 1
        total_chunks += len(chunks)
        if position % 25 == 0:
            print(f"  {position}/{len(items)} processed")
    await db.close_pool()
    print(f"done: {indexed} thesis indexed, {total_chunks} chunks "
          f"({metadata_only} fell back to metadata-only)")


if __name__ == "__main__":
    asyncio.run(main())
