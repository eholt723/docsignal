"""
Pre-loaded doc set definitions. Each preset has multiple targeted seed URLs
pointing directly at content relevant to the example questions.
"""
from backend.database import doc_set_exists
from backend.ingestion import ingest_url

PRESETS = {
    "fastapi": {
        "doc_name": "FastAPI Docs",
        "display_url": "https://fastapi.tiangolo.com/",
        "seeds": [
            {"url": "https://fastapi.tiangolo.com/tutorial/dependencies/", "max_pages": 10},
            {"url": "https://fastapi.tiangolo.com/tutorial/security/", "max_pages": 10},
            {"url": "https://fastapi.tiangolo.com/async/", "max_pages": 5},
            {"url": "https://fastapi.tiangolo.com/tutorial/", "max_pages": 15},
        ],
        "example_questions": [
            "How does dependency injection work and when should I use it over regular function parameters?",
            "What's the difference between async def and def route handlers and when does it matter?",
            "How do I implement OAuth2 password flow with JWT tokens?",
        ],
    },
    "sqlite": {
        "doc_name": "SQLite Docs",
        "display_url": "https://www.sqlite.org/",
        "seeds": [
            {"url": "https://www.sqlite.org/lang.html", "max_pages": 20},
            {"url": "https://www.sqlite.org/datatype3.html", "max_pages": 5},
            {"url": "https://www.sqlite.org/lang_with.html", "max_pages": 5},
            {"url": "https://www.sqlite.org/lockingv3.html", "max_pages": 5},
            {"url": "https://www.sqlite.org/wal.html", "max_pages": 5},
        ],
        "example_questions": [
            "What's the difference between TEXT, REAL, and INTEGER storage classes in SQLite?",
            "How do I use a CTE and when is it better than a subquery?",
            "How does SQLite handle concurrent reads and writes?",
        ],
    },
    "requests": {
        "doc_name": "Requests Docs",
        "display_url": "https://requests.readthedocs.io/en/latest/",
        "seeds": [
            {"url": "https://requests.readthedocs.io/en/latest/user/quickstart/", "max_pages": 10},
            {"url": "https://requests.readthedocs.io/en/latest/user/advanced/", "max_pages": 10},
            {"url": "https://requests.readthedocs.io/en/latest/api/", "max_pages": 8},
        ],
        "example_questions": [
            "How do I send authentication headers with a request?",
            "What's the difference between params and data in a POST request?",
            "How do I handle timeouts and retries?",
        ],
    },
}


def get_preset_definitions() -> dict:
    """Return preset metadata for the frontend."""
    return {
        key: {
            "doc_name": p["doc_name"],
            "url": p["display_url"],
            "example_questions": p["example_questions"],
        }
        for key, p in PRESETS.items()
    }


def ingest_preset(preset_key: str) -> dict:
    """Ingest all seed URLs for a preset. Skips if already ingested."""
    preset = PRESETS.get(preset_key)
    if not preset:
        raise ValueError(f"Unknown preset: {preset_key}")

    if doc_set_exists(preset_key):
        return {"skipped": True, "doc_name": preset["doc_name"]}

    total_chunks = 0
    doc_ids = []
    for i, seed in enumerate(preset["seeds"]):
        label = f"{preset['doc_name']} ({i + 1})"
        result = ingest_url(
            url=seed["url"],
            doc_name=label,
            doc_set=preset_key,
            max_pages=seed["max_pages"],
        )
        total_chunks += result["chunks_stored"]
        doc_ids.append(result["doc_id"])

    return {"doc_ids": doc_ids, "doc_name": preset["doc_name"], "chunks_stored": total_chunks}


def ingest_all_presets() -> list[dict]:
    """Ingest all presets. Called at startup if not already done."""
    return [ingest_preset(key) for key in PRESETS]
