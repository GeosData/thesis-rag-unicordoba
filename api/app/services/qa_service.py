from __future__ import annotations

import logging

from app.repositories import query_log_repository
from app.schemas.qa import AskResponse, Citation
from app.services.rag_graph import get_graph

logger = logging.getLogger(__name__)


async def answer_question(question: str) -> AskResponse:
    result = await get_graph().ainvoke({"question": question})
    response = AskResponse(
        answer=result["answer"],
        citations=[Citation(**citation) for citation in result.get("citations", [])],
        grounded=result["grounded"],
    )
    try:
        await query_log_repository.log_query(question, response.grounded, len(response.citations))
    except Exception:
        logger.warning("query logging failed", exc_info=True)
    return response
