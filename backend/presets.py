"""
Pre-loaded doc set definitions. Call ingest_all_presets() once on first startup
if presets are not yet in the database.
"""
from backend.database import get_document_by_name
from backend.ingestion import ingest_url

PRESETS = {
    "fastapi": {
        "doc_name": "FastAPI Docs",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "example_questions": [
            "How does dependency injection work and when should I use it over regular function parameters?",
            "What's the difference between async def and def route handlers and when does it matter?",
            "How do I implement OAuth2 password flow with JWT tokens?",
        ],
    },
    "langchain": {
        "doc_name": "LangChain Docs",
        "url": "https://python.langchain.com/docs/how_to/",
        "example_questions": [
            "What's the difference between a Chain and an Agent and when should I use each?",
            "How do I add memory to a conversational chain so it remembers previous messages?",
            "How does LangChain handle streaming responses from an LLM?",
        ],
    },
    "postgresql": {
        "doc_name": "PostgreSQL Docs",
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
        "example_questions": [
            "What's the difference between an inner join and a left join and when would I use each?",
            "How do indexes work and how do I know when to add one?",
            "What is a CTE and how is it different from a subquery?",
        ],
    },
}


def get_preset_definitions() -> dict:
    """Return preset metadata (names, example questions) for the frontend."""
    return {
        key: {
            "doc_name": p["doc_name"],
            "url": p["url"],
            "example_questions": p["example_questions"],
        }
        for key, p in PRESETS.items()
    }


def ingest_preset(preset_key: str) -> dict:
    """Ingest a single preset by key. Skips if already ingested."""
    preset = PRESETS.get(preset_key)
    if not preset:
        raise ValueError(f"Unknown preset: {preset_key}")

    existing = get_document_by_name(preset["doc_name"])
    if existing:
        return {"skipped": True, "doc_name": preset["doc_name"]}

    result = ingest_url(
        url=preset["url"],
        doc_name=preset["doc_name"],
        doc_set=preset_key,
        max_pages=50,
    )
    return result


def ingest_all_presets() -> list[dict]:
    """Ingest all presets. Called at startup if not already done."""
    results = []
    for key in PRESETS:
        result = ingest_preset(key)
        results.append(result)
    return results
