from __future__ import annotations

import asyncio

from app.config.settings import get_settings
from app.repositories import db, thesis_repository
from app.services import corpus, embeddings


async def main() -> None:
    settings = get_settings()
    items = corpus.load_corpus(settings.corpus_path)
    print(f"corpus: {len(items)} thesis")
    await db.get_pool()
    indexed = 0
    for position, item in enumerate(items, start=1):
        document = corpus.build_document(item)
        if not document:
            continue
        chunks = corpus.chunk_text(document)
        vectors = embeddings.embed_passages(chunks)
        await thesis_repository.upsert_thesis(item)
        await thesis_repository.replace_chunks(item["uuid"], chunks, vectors)
        indexed += 1
        if position % 25 == 0:
            print(f"  {position}/{len(items)} processed")
    await db.close_pool()
    print(f"done: {indexed} thesis indexed")


if __name__ == "__main__":
    asyncio.run(main())
