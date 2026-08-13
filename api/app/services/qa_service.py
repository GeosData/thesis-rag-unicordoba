from __future__ import annotations

from app.schemas.qa import AskResponse, Citation
from app.services.rag_graph import get_graph


async def answer_question(question: str) -> AskResponse:
    result = await get_graph().ainvoke({"question": question})
    return AskResponse(
        answer=result["answer"],
        citations=[Citation(**citation) for citation in result.get("citations", [])],
        grounded=result["grounded"],
    )
