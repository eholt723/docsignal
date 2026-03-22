---
title: DocSignal
emoji: 📄
colorFrom: blue
colorTo: blue
sdk: docker
pinned: false
---

![CI](https://github.com/eholt723/docsignal/actions/workflows/ci.yml/badge.svg)

# DocSignal

AI-powered documentation intelligence. Ask natural language questions against any documentation set — DocSignal finds the meaning, not just the keywords.

A keyword search for "authentication" returns every page that mentions the word. DocSignal understands what you're asking and returns the most semantically relevant answer with the exact source passage cited.

**Live demo:** [Hugging Face Spaces](https://huggingface.co/spaces/eholt723/docsignal)

---

## Features

- Ask questions against FastAPI, SQLite, and Requests docs out of the box — no setup
- Upload any PDF or crawl any URL (up to 25 pages) to build a custom doc set
- Every answer includes cited source passages with similarity scores
- Analytics dashboard: query frequency, top sources, volume over time, similarity distribution
- Embedding provider switchable between local (fastembed) and OpenAI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI |
| Frontend | React 18, Vite, Tailwind CSS |
| LLM | Groq — llama-3.1-8b-instant (OpenAI-compatible) |
| Embeddings | fastembed — BAAI/bge-small-en-v1.5 (384 dims, runs locally) |
| Vector DB | pgvector extension on PostgreSQL |
| Database | PostgreSQL (local Docker) / Neon serverless (production) |
| Charts | Recharts |
| Hosting | Hugging Face Spaces (port 7860) |

---

## Architecture

```
PDF / URL (max 25 pages)
        │
        ▼
┌───────────────────┐
│  Ingestion        │  Extract text, split into 512-token chunks (64-token overlap)
│  (ingestion.py)   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Embedding        │  fastembed BAAI/bge-small-en-v1.5 → 384-dim vectors
│  (embeddings.py)  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  pgvector DB      │  Store vectors + source metadata (doc name, URL, chunk text)
│  (database.py)    │
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────────────┐
│ Search │  │ Q&A pipeline     │  Retrieve top-k chunks via cosine similarity →
│  API   │  │ (qa.py)          │  Groq synthesizes answer → return + citations
└────────┘  └──────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ React frontend   │  Presets, example questions, cited answers, dashboard
          └──────────────────┘
```

| Layer | Responsibility |
|---|---|
| Ingestion | Extract text from PDF or URL, split into overlapping chunks |
| Embedding | Generate dense vector per chunk via fastembed (local, no API key) |
| pgvector | Store vectors, cosine similarity search (`<=>` operator) |
| Search API | Embed query, retrieve top-k similar chunks |
| Q&A pipeline | Feed chunks to Groq LLM, return synthesized answer + citations |
| Analytics | SQL aggregations over query history (frequency, sources, trends) |
| Frontend | Preset buttons, example questions, cited answer UI, Recharts dashboard |

---

## Project Structure

```
docsignal/
├── backend/
│   ├── main.py          # FastAPI app, all route definitions
│   ├── ingestion.py     # PDF/URL extraction and chunking pipeline
│   ├── embeddings.py    # fastembed wrapper, query embedding
│   ├── database.py      # pgvector connection, schema init, similarity search
│   ├── qa.py            # Q&A: retrieve chunks → Groq synthesis → cited answer
│   ├── analytics.py     # SQL aggregation queries for dashboard
│   ├── presets.py       # Pre-loaded doc set definitions and ingestion logic
│   └── models.py        # Pydantic request/response schemas
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── PresetBar.jsx        # FastAPI / SQLite / Requests selector
│           ├── ExampleQuestions.jsx # Clickable example question chips
│           ├── AskPanel.jsx         # Q&A input, answer display, citations
│           ├── UploadPanel.jsx      # PDF upload and URL ingestion form
│           ├── Dashboard.jsx        # Analytics charts layout
│           └── About.jsx            # Employer-facing showcase page
├── tests/
│   ├── unit/            # Chunking, embedding shape, route tests
│   └── integration/     # Full ingest → search → ask lifecycle
├── Dockerfile           # Multi-stage: Vite build → FastAPI serve on port 7860
├── docker-compose.yml   # Local dev: app + postgres+pgvector
├── pyproject.toml
└── .env.example
```

---

## Local Development

**Prerequisites:** Docker, Node.js 20, Python 3.11

```bash
# 1. Clone and set up environment
git clone https://github.com/eholt723/docsignal.git
cd docsignal
cp .env.example .env
# Edit .env — set GROQ_API_KEY (free at console.groq.com)

# 2. Start the database
docker compose up db -d

# 3. Install and start the backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn backend.main:app --reload --port 8000

# 4. Install and start the frontend (separate terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173

# 5. Ingest a preset doc set (first time only)
curl -X POST http://localhost:8000/api/presets/fastapi/ingest
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `GROQ_API_KEY` | Yes | Groq API key — free at console.groq.com |
| `EMBEDDING_PROVIDER` | No | `fastembed` (default) or `openai` |

---

## Deployment (Hugging Face Spaces)

1. Create a new Space — type: Docker
2. Push this repo to the Space's git remote
3. Set Secrets: `DATABASE_URL` (Neon connection string), `GROQ_API_KEY`
4. The Dockerfile builds the frontend and serves everything on port 7860

**Neon setup:** Create a free project at neon.tech, then run once:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
The app creates all tables on first startup.

---

## Running Tests

```bash
pytest tests/unit/
pytest tests/integration/   # requires DATABASE_URL pointing to a live DB
```
