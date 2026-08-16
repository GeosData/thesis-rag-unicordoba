from __future__ import annotations

import asyncio
import time
from statistics import mean, median

from app.config.settings import get_settings
from app.repositories import db, retrieval_repository
from app.services import embeddings, rag_graph

from eval.dataset_adversarial import ADVERSARIAL
from eval.dataset_content import GOLD_CONTENT

QUERIES = [item["q"] for item in GOLD_CONTENT] + list(ADVERSARIAL)


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(0.95 * len(ordered)))]


async def main() -> None:
    await db.get_pool()
    top_k = get_settings().retrieval_top_k
    embed_ms, retrieve_ms, grade_ms, total_ms = [], [], [], []
    generate_ms: list[float] = []
    context_chars: list[int] = []

    for question in QUERIES:
        t = time.perf_counter()
        vector = embeddings.embed_query(question)
        embed = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        contexts = await retrieval_repository.hybrid_search(question, vector, top_k)
        retrieve = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        graded = await rag_graph.grade({"question": question, "contexts": contexts})
        grade = (time.perf_counter() - t) * 1000

        generate = 0.0
        if graded["grounded"]:
            t = time.perf_counter()
            await rag_graph.generate({"question": question, "contexts": contexts})
            generate = (time.perf_counter() - t) * 1000
            generate_ms.append(generate)
            context_chars.append(sum(len(c["content"]) for c in contexts))

        embed_ms.append(embed)
        retrieve_ms.append(retrieve)
        grade_ms.append(grade)
        total_ms.append(embed + retrieve + grade + generate)

    print(f"latency per stage (ms) over {len(QUERIES)} queries "
          f"({len(generate_ms)} reached generate, {len(QUERIES) - len(generate_ms)} refused at grade)\n")
    print(f"{'stage':<12}{'p50':>8}{'p95':>8}{'mean':>8}")
    for name, values in [("embed", embed_ms), ("retrieve", retrieve_ms),
                         ("grade", grade_ms), ("generate", generate_ms), ("total", total_ms)]:
        if values:
            print(f"{name:<12}{median(values):>8.0f}{_p95(values):>8.0f}{mean(values):>8.0f}")

    grade_share = 100 * sum(grade_ms) / sum(total_ms)
    print(f"\ngrade-by-LLM share of total wall time: {grade_share:.0f}%")
    if context_chars:
        approx_tokens = mean(context_chars) / 4
        print(f"generate input context: ~{mean(context_chars):.0f} chars (~{approx_tokens:.0f} tokens) avg — proxy for cost")
    await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
