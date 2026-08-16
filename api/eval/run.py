from __future__ import annotations

import asyncio
import time

from app.repositories import db, retrieval_repository
from app.services import embeddings

from eval.dataset import GOLD, GoldItem
from eval.metrics import dedupe_keep_order, recall_at_k, reciprocal_rank

RETRIEVE_K = 10
REPORT_KS = (1, 3, 5)


async def _vector_only(query: str, vector: list[float]) -> list[str]:
    rows = await retrieval_repository.search(vector, k=RETRIEVE_K)
    return dedupe_keep_order(row["handle"] for row in rows)


async def _hybrid_rrf(query: str, vector: list[float]) -> list[str]:
    rows = await retrieval_repository.hybrid_search(query, vector, k=RETRIEVE_K)
    return dedupe_keep_order(row["handle"] for row in rows)


RETRIEVERS = {
    "vector-only": _vector_only,
    "hybrid-rrf": _hybrid_rrf,
}


async def _score_retriever(name, retrieve) -> dict:
    recalls = {k: [] for k in REPORT_KS}
    rrs: list[float] = []
    latencies: list[float] = []
    misses: list[str] = []
    for item in GOLD:
        vector = embeddings.embed_query(item["q"])
        started = time.perf_counter()
        handles = await retrieve(item["q"], vector)
        latencies.append((time.perf_counter() - started) * 1000)
        relevant = item["relevant_handles"]
        for k in REPORT_KS:
            recalls[k].append(recall_at_k(relevant, handles, k))
        rr = reciprocal_rank(relevant, handles)
        rrs.append(rr)
        if rr == 0.0:
            misses.append(item["note"])
    size = len(GOLD)
    return {
        "name": name,
        "recall": {k: sum(recalls[k]) / size for k in REPORT_KS},
        "mrr": sum(rrs) / size,
        "p50_ms": sorted(latencies)[size // 2],
        "misses": misses,
    }


def _print_report(results: list[dict]) -> None:
    header = f"{'retriever':<14}" + "".join(f"recall@{k:<5}" for k in REPORT_KS) + f"{'mrr':<8}{'p50 ms':<8}"
    print("\n" + header)
    print("-" * len(header))
    for r in results:
        row = f"{r['name']:<14}"
        row += "".join(f"{r['recall'][k]:<8.3f}" for k in REPORT_KS)
        row += f"{r['mrr']:<8.3f}{r['p50_ms']:<8.0f}"
        print(row)
    print()
    for r in results:
        if r["misses"]:
            print(f"{r['name']} missed (rank 0): {', '.join(r['misses'])}")


async def main() -> None:
    await db.get_pool()
    print(f"gold questions: {len(GOLD)} | retrieve_k={RETRIEVE_K} | metric: thesis-level (handle)")
    results = [await _score_retriever(name, fn) for name, fn in RETRIEVERS.items()]
    _print_report(results)
    await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
