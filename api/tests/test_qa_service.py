import pytest

from app.schemas.qa import Answer, Citation
from app.services import qa_service
from app.services.rag_graph import Relevance

from tests.conftest import make_chunk


async def test_grounded_response_has_citations_and_is_logged(pipeline):
    pipeline.retrieval.rows = [make_chunk()]
    pipeline.llm.responses["Relevance"] = Relevance(relevant=True)
    pipeline.llm.responses["Answer"] = Answer(
        answer="ok", citations=[Citation(title="Tesis uno", handle="ucordoba/1")]
    )
    response = await qa_service.answer_question("q")
    assert response.grounded is True
    assert [c.handle for c in response.citations] == ["ucordoba/1"]
    assert pipeline.query_log.entries == [("q", True, 1)]


async def test_fallback_response_is_ungrounded_without_citations(pipeline):
    pipeline.retrieval.rows = []
    response = await qa_service.answer_question("q")
    assert response.grounded is False
    assert response.citations == []
    assert pipeline.query_log.entries == [("q", False, 0)]


async def test_query_log_failure_does_not_break_answer(pipeline):
    pipeline.retrieval.rows = []
    pipeline.query_log.error = RuntimeError("log db down")
    response = await qa_service.answer_question("q")
    assert response.grounded is False


async def test_graph_error_propagates_and_nothing_is_logged(pipeline):
    pipeline.retrieval.error = RuntimeError("db down")
    with pytest.raises(RuntimeError):
        await qa_service.answer_question("q")
    assert pipeline.query_log.entries == []
