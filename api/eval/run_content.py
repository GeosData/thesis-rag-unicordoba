from __future__ import annotations

import asyncio

from app.repositories import db, retrieval_repository
from app.services import embeddings

from eval.dataset_content import GOLD_CONTENT
from eval.metrics import content_hit_at_k

RETRIEVE_K = 10
REPORT_KS = (1, 3, 5)


async def _vector_only(query: str, vector: list[float]) -> list[dict]:
    return await retrieval_repository.search(vector, k=RETRIEVE_K)


async def _hybrid_rrf(query: str, vector: list[float]) -> list[dict]:
    return await retrieval_repository.hybrid_search(query, vector, k=RETRIEVE_K)


RETRIEVERS = {"vector-only": _vector_only, "hybrid-rrf": _hybrid_rrf}


async def _score(name, retrieve) -> dict:
    hits = {k: [] for k in REPORT_KS}
    misses: list[str] = []
    for item in GOLD_CONTENT:
        vector = embeddings.embed_query(item["q"])
        results = await retrieve(item["q"], vector)
        for k in REPORT_KS:
            hits[k].append(content_hit_at_k(results, item["handle"], item["must_contain"], k))
        if not content_hit_at_k(results, item["handle"], item["must_contain"], REPORT_KS[-1]):
            misses.append(item["note"])
    size = len(GOLD_CONTENT)
    return {
        "name": name,
        "hit": {k: sum(hits[k]) / size for k in REPORT_KS},
        "misses": misses,
    }


def _report(results: list[dict]) -> None:
    header = f"{'retriever':<14}" + "".join(f"hit@{k:<6}" for k in REPORT_KS)
    print("\n" + header)
    print("-" * len(header))
    for r in results:
        row = f"{r['name']:<14}" + "".join(f"{r['hit'][k]:<7.3f}" for k in REPORT_KS)
        print(row)
    print()
    for r in results:
        if r["misses"]:
            print(f"{r['name']} missed: {', '.join(r['misses'])}")


async def main() -> None:
    await db.get_pool()
    print(f"content gold: {len(GOLD_CONTENT)} questions | metric: content-hit (right thesis chunk contains the answer)")
    results = [await _score(name, fn) for name, fn in RETRIEVERS.items()]
    _report(results)
    await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
