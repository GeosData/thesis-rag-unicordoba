from __future__ import annotations

import asyncio
import sys

from app.repositories import db, retrieval_repository
from app.services import embeddings


async def main(query: str, k: int = 5) -> None:
    await db.get_pool()
    vector = embeddings.embed_query(query)
    results = await retrieval_repository.search(vector, k)
    print(f"query: {query}\n")
    for result in results:
        print(f"[{result['score']:.3f}] {result['title']} ({result['year']}) — {result['author']}")
        print(f"   {result['content'][:180].strip()}...")
        print(f"   {result['handle']}\n")
    await db.close_pool()


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "aplicacion movil para tiendas de barrio"
    asyncio.run(main(question))
