import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import init_db
from backend.models import (
    IngestRequest, IngestResponse,
    SearchRequest, SearchResponse, ChunkResult,
    AskRequest, AskResponse, Citation,
    AnalyticsOverview, TopQuestion, TopSource, QueryVolume, SimilarityBucket,
)
from backend.ingestion import ingest_pdf, ingest_url
from backend.embeddings import embed_query
from backend.database import similarity_search
from backend.qa import ask
from backend import analytics
from backend.presets import get_preset_definitions


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="DocSignal", lifespan=lifespan)


# ── Ingest ───────────────────────────────────────────────────────────────────

@app.post("/api/ingest/url", response_model=IngestResponse)
def ingest_from_url(body: IngestRequest):
    try:
        result = ingest_url(url=body.url, doc_name=body.doc_name, max_pages=25)
        return IngestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest/pdf", response_model=IngestResponse)
async def ingest_from_pdf(
    file: UploadFile = File(...),
    doc_name: str = Form(None),
):
    file_bytes = await file.read()
    name = doc_name or file.filename or "uploaded.pdf"
    try:
        result = ingest_pdf(file_bytes=file_bytes, doc_name=name)
        return IngestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Search ───────────────────────────────────────────────────────────────────

@app.post("/api/search", response_model=SearchResponse)
def search(body: SearchRequest):
    try:
        query_vec = embed_query(body.query)
        chunks = similarity_search(query_vec, doc_set=body.doc_set, top_k=body.top_k)
        results = [ChunkResult(**c) for c in chunks]
        return SearchResponse(query=body.query, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Q&A ──────────────────────────────────────────────────────────────────────

@app.post("/api/ask", response_model=AskResponse)
def ask_question(body: AskRequest):
    try:
        result = ask(question=body.question, doc_set=body.doc_set, top_k=body.top_k)
        # Serialize citations
        result["citations"] = [
            c if isinstance(c, dict) else c.model_dump()
            for c in result["citations"]
        ]
        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Presets ──────────────────────────────────────────────────────────────────

@app.get("/api/presets")
def get_presets():
    return get_preset_definitions()


@app.post("/api/presets/{preset_key}/ingest")
def trigger_preset_ingest(preset_key: str):
    from backend.presets import ingest_preset
    try:
        result = ingest_preset(preset_key)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Analytics ────────────────────────────────────────────────────────────────

@app.get("/api/analytics/overview", response_model=AnalyticsOverview)
def analytics_overview():
    return analytics.get_overview()


@app.get("/api/analytics/top-questions")
def top_questions(limit: int = 10):
    return analytics.get_top_questions(limit=limit)


@app.get("/api/analytics/top-sources")
def top_sources(limit: int = 10):
    return analytics.get_top_sources(limit=limit)


@app.get("/api/analytics/query-volume")
def query_volume(days: int = 30):
    return analytics.get_query_volume(days=days)


@app.get("/api/analytics/similarity-distribution")
def similarity_distribution():
    return analytics.get_similarity_distribution()


# ── Serve React frontend ──────────────────────────────────────────────────────

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        index = os.path.join(STATIC_DIR, "index.html")
        return FileResponse(index)
