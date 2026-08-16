from __future__ import annotations

import asyncio

from app.repositories import db
from app.services import rag_graph

from eval.dataset_adversarial import ADVERSARIAL
from eval.metrics import strip_accents

REFUSAL_MARKERS = (
    "no encontr", "no hay evidencia", "no hay informacion", "no hay datos",
    "no alcanza", "no dispone", "no se encuentra", "no aparece", "contexto no",
    "no es posible responder", "no proporciona", "no menciona", "no contiene",
    "sin evidencia", "no se menciona", "no se proporciona",
)


def _is_refusal(grounded: bool, answer: str) -> bool:
    if not grounded:
        return True
    stripped = strip_accents(answer)
    return any(marker in stripped for marker in REFUSAL_MARKERS)


async def main() -> None:
    await db.get_pool()
    graph = rag_graph.get_graph()
    refused = 0
    for question in ADVERSARIAL:
        state = await graph.ainvoke({"question": question})
        grounded = state.get("grounded", False)
        answer = state.get("answer", "")
        best_cosine = max((c.get("cosine", 0.0) for c in state.get("contexts", [])), default=0.0)
        ok = _is_refusal(grounded, answer)
        refused += ok
        tag = "REFUSED " if ok else "ANSWERED"
        print(f"{tag} grounded={grounded} best_cos={best_cosine:.2f} :: {question[:55]}")
        print(f"         -> {answer[:110].strip()}")
    total = len(ADVERSARIAL)
    print(f"\nrefusal rate: {refused}/{total} = {refused / total:.3f} (higher is better)")
    await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
