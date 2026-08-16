from __future__ import annotations

from collections.abc import Iterable


def dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def recall_at_k(relevant: Iterable[str], retrieved: list[str], k: int) -> float:
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    top_k = set(retrieved[:k])
    return len(relevant_set & top_k) / len(relevant_set)


def precision_at_k(relevant: Iterable[str], retrieved: list[str], k: int) -> float:
    if k == 0:
        return 0.0
    relevant_set = set(relevant)
    hits = sum(1 for doc in retrieved[:k] if doc in relevant_set)
    return hits / k


def reciprocal_rank(relevant: Iterable[str], retrieved: list[str]) -> float:
    relevant_set = set(relevant)
    for position, doc in enumerate(retrieved, start=1):
        if doc in relevant_set:
            return 1.0 / position
    return 0.0
