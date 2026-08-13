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
