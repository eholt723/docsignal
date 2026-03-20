"""
Integration tests — require a real PostgreSQL+pgvector instance.
Set DATABASE_URL env var pointing to a test database before running.

Run with: pytest tests/integration/ -v
Skip with: pytest tests/unit/ (unit tests only)
"""
import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set — skipping integration tests",
)


@pytest.fixture(scope="module")
def db():
    from backend.database import init_db, get_conn
    init_db()
    yield
    # Cleanup: drop test data inserted during tests
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM documents WHERE doc_name LIKE 'test_%';")
    conn.commit()
    cur.close()
    conn.close()


def test_ingest_and_search(db):
    from backend.ingestion import _store, _chunk_text
    from backend.embeddings import embed_query
    from backend.database import similarity_search

    text = "FastAPI is a modern web framework for building APIs with Python."
    chunks = _chunk_text(text)
    assert chunks

    doc_id = _store(
        doc_name="test_fastapi_mini",
        source_url=None,
        doc_set="test",
        chunks_text=chunks,
    )
    assert doc_id > 0

    query_vec = embed_query("What is FastAPI?")
    results = similarity_search(query_vec, doc_set="test", top_k=3)
    assert len(results) > 0
    assert results[0]["similarity"] > 0.0
    assert "FastAPI" in results[0]["text"]


def test_query_logging(db):
    from backend.database import log_query, get_conn
    log_query("What is FastAPI?", "test", 0.87)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM query_logs WHERE query_text = 'What is FastAPI?';")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    assert count >= 1
