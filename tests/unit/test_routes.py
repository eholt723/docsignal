"""Route tests via FastAPI TestClient — DB and embeddings mocked."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with patch("backend.database.init_db"), \
         patch("backend.database.get_conn"):
        from backend.main import app
        return TestClient(app)


def test_get_presets(client):
    resp = client.get("/api/presets")
    assert resp.status_code == 200
    data = resp.json()
    assert "fastapi" in data
    assert "langchain" in data
    assert "postgresql" in data
    for key, preset in data.items():
        assert "doc_name" in preset
        assert "example_questions" in preset
        assert len(preset["example_questions"]) == 3


@patch("backend.main.embed_query", return_value=[0.1] * 384)
@patch("backend.main.similarity_search", return_value=[])
def test_search_empty_results(mock_search, mock_embed, client):
    resp = client.post("/api/search", json={"query": "test", "doc_set": "fastapi"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "test"
    assert data["results"] == []


@patch("backend.main.ask", return_value={
    "question": "test?",
    "answer": "test answer",
    "citations": [],
})
def test_ask_returns_answer(mock_ask, client):
    resp = client.post("/api/ask", json={"question": "test?", "doc_set": "fastapi"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "test answer"
    assert "citations" in data


def test_analytics_overview_structure(client):
    with patch("backend.analytics.get_overview", return_value={
        "total_queries": 0, "total_chunks": 0, "total_documents": 0
    }):
        resp = client.get("/api/analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_queries" in data
        assert "total_chunks" in data
        assert "total_documents" in data
