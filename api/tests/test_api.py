from fastapi.testclient import TestClient

from app.main import app


def test_health_ok():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == "scholar-rag"


def test_ask_validates_missing_question():
    with TestClient(app) as client:
        response = client.post("/ask", json={})
        assert response.status_code == 422


def test_ask_rejects_oversized_question():
    with TestClient(app) as client:
        response = client.post("/ask", json={"question": "a" * 2001})
        assert response.status_code == 422


def test_ask_rejects_non_string_question():
    with TestClient(app) as client:
        assert client.post("/ask", json={"question": 123}).status_code == 422
        assert client.post("/ask", json={"question": None}).status_code == 422


def test_ask_rejects_malformed_json():
    with TestClient(app) as client:
        response = client.post(
            "/ask", content="{not json", headers={"content-type": "application/json"}
        )
        assert response.status_code == 422


def test_ask_returns_grounded_answer_with_citation(pipeline):
    from app.schemas.qa import Answer, Citation
    from app.services.rag_graph import Relevance
    from tests.conftest import make_chunk

    pipeline.retrieval.rows = [make_chunk()]
    pipeline.llm.responses["Relevance"] = Relevance(relevant=True)
    pipeline.llm.responses["Answer"] = Answer(
        answer="ok", citations=[Citation(title="Tesis uno", handle="ucordoba/1")]
    )
    with TestClient(app) as client:
        response = client.post("/ask", json={"question": "que es X?"})
    assert response.status_code == 200
    assert response.json() == {
        "answer": "ok",
        "citations": [{"title": "Tesis uno", "handle": "ucordoba/1"}],
        "grounded": True,
    }


def test_ask_returns_fallback_when_no_evidence(pipeline):
    pipeline.retrieval.rows = []
    with TestClient(app) as client:
        response = client.post("/ask", json={"question": "tema inexistente"})
    body = response.json()
    assert response.status_code == 200
    assert body["grounded"] is False
    assert body["citations"] == []
    assert "No encontre evidencia" in body["answer"]


def test_ask_backend_failure_returns_500_without_leaking_details(pipeline):
    pipeline.retrieval.error = RuntimeError("secret-dsn postgres://user:pw@host")
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/ask", json={"question": "q"})
    assert response.status_code == 500
    assert "secret-dsn" not in response.text


def test_ask_is_rate_limited(pipeline):
    pipeline.retrieval.rows = []
    with TestClient(app) as client:
        statuses = [client.post("/ask", json={"question": "q"}).status_code for _ in range(11)]
    assert statuses[:10] == [200] * 10
    assert statuses[10] == 429
