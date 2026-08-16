from __future__ import annotations

import asyncio
import time

from app.config.settings import get_settings
from app.repositories import db, retrieval_repository
from app.services import embeddings

from eval.dataset_adversarial import ADVERSARIAL
from eval.dataset_content import GOLD_CONTENT

POOL = [item["q"] for item in GOLD_CONTENT] + list(ADVERSARIAL)
LEVELS = (1, 5, 10, 20)


async def _one(question: str, top_k: int) -> None:
    vector = embeddings.embed_query(question)          # CPU-bound, blocks the event loop (GIL)
    await retrieval_repository.hybrid_search(question, vector, top_k)


async def main() -> None:
    await db.get_pool()
    top_k = get_settings().retrieval_top_k
    await _one(POOL[0], top_k)  # warm the model so cold-start doesn't skew level 1

    print("retrieval (embed+search) under concurrency — LLM excluded on purpose\n")
    print(f"{'concurrency':>11}{'wall ms':>10}{'throughput q/s':>16}{'ms/query':>11}")
    for level in LEVELS:
        batch = [POOL[i % len(POOL)] for i in range(level)]
        started = time.perf_counter()
        await asyncio.gather(*(_one(q, top_k) for q in batch))
        wall = (time.perf_counter() - started) * 1000
        throughput = level / (wall / 1000)
        print(f"{level:>11}{wall:>10.0f}{throughput:>16.1f}{wall / level:>11.0f}")

    print(f"\npool max_size={5} (db.py), embed_query is sync/CPU-bound")
    await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
