"""
SQL aggregation queries powering the analytics dashboard.
"""
import psycopg2.extras
from backend.database import get_conn


def get_overview() -> dict:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) AS total_queries FROM query_logs;")
    total_queries = cur.fetchone()["total_queries"]
    cur.execute("SELECT COUNT(*) AS total_chunks FROM chunks;")
    total_chunks = cur.fetchone()["total_chunks"]
    cur.execute("SELECT COUNT(*) AS total_documents FROM documents;")
    total_documents = cur.fetchone()["total_documents"]
    cur.close()
    conn.close()
    return {
        "total_queries": total_queries,
        "total_chunks": total_chunks,
        "total_documents": total_documents,
    }


def get_top_questions(limit: int = 10) -> list[dict]:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT query_text, COUNT(*) AS count
        FROM query_logs
        GROUP BY query_text
        ORDER BY count DESC
        LIMIT %s;
        """,
        (limit,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_top_sources(limit: int = 10) -> list[dict]:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # Approximate citation count: count chunks per document queried
    cur.execute(
        """
        SELECT d.doc_name, COUNT(c.id) AS citation_count
        FROM documents d
        JOIN chunks c ON c.doc_id = d.id
        GROUP BY d.doc_name
        ORDER BY citation_count DESC
        LIMIT %s;
        """,
        (limit,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_query_volume(days: int = 30) -> list[dict]:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT DATE(queried_at) AS date, COUNT(*) AS count
        FROM query_logs
        WHERE queried_at >= NOW() - INTERVAL '%s days'
        GROUP BY DATE(queried_at)
        ORDER BY date;
        """,
        (days,),
    )
    rows = [{"date": str(r["date"]), "count": r["count"]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_similarity_distribution() -> list[dict]:
    """Bucket top_similarity scores into 0.1-wide ranges."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT
            CONCAT(
                CAST(FLOOR(top_similarity * 10) / 10 AS VARCHAR), '–',
                CAST(FLOOR(top_similarity * 10) / 10 + 0.1 AS VARCHAR)
            ) AS bucket,
            COUNT(*) AS count
        FROM query_logs
        WHERE top_similarity IS NOT NULL
        GROUP BY FLOOR(top_similarity * 10)
        ORDER BY FLOOR(top_similarity * 10);
        """
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows
