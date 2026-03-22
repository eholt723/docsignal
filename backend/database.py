import os
import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/docsignal")


def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    return conn


def _plain_conn():
    """Connection without vector registration — used before extension exists."""
    return psycopg2.connect(DATABASE_URL)


def init_db():
    # Create extension first using a plain connection (vector type not yet registered)
    conn = _plain_conn()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            doc_name TEXT NOT NULL,
            source_url TEXT,
            doc_set TEXT,
            ingested_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            embedding vector(384)
        );
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON chunks USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id SERIAL PRIMARY KEY,
            query_text TEXT NOT NULL,
            doc_set TEXT,
            top_similarity FLOAT,
            queried_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def insert_document(doc_name: str, source_url: str | None, doc_set: str | None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (doc_name, source_url, doc_set) VALUES (%s, %s, %s) RETURNING id;",
        (doc_name, source_url, doc_set),
    )
    doc_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return doc_id


def insert_chunks(doc_id: int, chunks: list[dict]):
    """chunks: list of {chunk_index, text, embedding}"""
    conn = get_conn()
    cur = conn.cursor()
    psycopg2.extras.execute_values(
        cur,
        "INSERT INTO chunks (doc_id, chunk_index, text, embedding) VALUES %s;",
        [(doc_id, c["chunk_index"], c["text"], c["embedding"]) for c in chunks],
    )
    conn.commit()
    cur.close()
    conn.close()


def similarity_search(query_embedding, doc_set: str | None, top_k: int) -> list[dict]:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if doc_set:
        cur.execute(
            """
            SELECT c.id AS chunk_id, d.doc_name, d.source_url,
                   c.text, 1 - (c.embedding <=> %s::vector) AS similarity
            FROM chunks c
            JOIN documents d ON d.id = c.doc_id
            WHERE d.doc_set = %s
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s;
            """,
            (query_embedding, doc_set, query_embedding, top_k),
        )
    else:
        cur.execute(
            """
            SELECT c.id AS chunk_id, d.doc_name, d.source_url,
                   c.text, 1 - (c.embedding <=> %s::vector) AS similarity
            FROM chunks c
            JOIN documents d ON d.id = c.doc_id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s;
            """,
            (query_embedding, query_embedding, top_k),
        )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def log_query(query_text: str, doc_set: str | None, top_similarity: float | None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO query_logs (query_text, doc_set, top_similarity) VALUES (%s, %s, %s);",
        (query_text, doc_set, top_similarity),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_document_by_name(doc_name: str) -> dict | None:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM documents WHERE doc_name = %s LIMIT 1;", (doc_name,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None
