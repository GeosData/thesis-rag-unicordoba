from __future__ import annotations

import asyncio

from pydantic import BaseModel, Field

from app.repositories import db
from app.services import llm, rag_graph

from eval.dataset_content import GOLD_CONTENT


class Judgment(BaseModel):
    total_claims: int = Field(description="numero de afirmaciones factuales atomicas en la respuesta")
    supported_claims: int = Field(description="cuantas estan respaldadas directamente por el contexto")
    unsupported: list[str] = Field(default_factory=list, description="afirmaciones no respaldadas por el contexto")


def _context_block(contexts: list[dict]) -> str:
    return "\n\n".join(f"[{c['handle']}] {c['content']}" for c in contexts)


async def _faithfulness(answer: str, contexts: list[dict], judge) -> float | None:
    prompt = (
        "Evalua la fidelidad (faithfulness) de una respuesta de un sistema RAG. "
        "Descompon la RESPUESTA en afirmaciones factuales atomicas y marca cada una como "
        "soportada solo si el CONTEXTO la respalda directamente. Devuelve total_claims, "
        "supported_claims y las afirmaciones no soportadas.\n\n"
        f"CONTEXTO:\n{_context_block(contexts)}\n\n"
        f"RESPUESTA:\n{answer}"
    )
    judgment: Judgment = await judge.ainvoke(prompt)
    if judgment.total_claims == 0:
        return None
    return judgment.supported_claims / judgment.total_claims


async def main() -> None:
    await db.get_pool()
    judge = llm.get_llm().with_structured_output(Judgment, method="function_calling")
    graph = rag_graph.get_graph()
    scores: list[float] = []
    for item in GOLD_CONTENT:
        state = await graph.ainvoke({"question": item["q"]})
        if not state.get("grounded") or not state.get("contexts"):
            print(f"[fallback]        {item['note']}")
            continue
        score = await _faithfulness(state["answer"], state["contexts"], judge)
        if score is None:
            continue
        scores.append(score)
        print(f"faith={score:.2f}  {item['note']}: {state['answer'][:80].strip()}")
    if scores:
        print(f"\nmean faithfulness: {sum(scores) / len(scores):.3f} over {len(scores)} grounded answers")
    await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
