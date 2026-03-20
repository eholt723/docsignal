"""
Ingestion pipeline: extract text from PDF or URL, split into chunks,
generate embeddings, store in pgvector.
"""
import io
import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pypdf import PdfReader

from backend.embeddings import embed_texts
from backend.database import insert_document, insert_chunks

CHUNK_SIZE = 512      # tokens (approximated as ~4 chars/token → ~2048 chars)
CHUNK_OVERLAP = 64   # tokens overlap (~256 chars)

CHARS_PER_TOKEN = 4
CHUNK_CHARS = CHUNK_SIZE * CHARS_PER_TOKEN
OVERLAP_CHARS = CHUNK_OVERLAP * CHARS_PER_TOKEN


def ingest_pdf(file_bytes: bytes, doc_name: str, doc_set: str | None = None) -> dict:
    text = _extract_pdf_text(file_bytes)
    chunks_text = _chunk_text(text)
    doc_id = _store(doc_name=doc_name, source_url=None, doc_set=doc_set, chunks_text=chunks_text)
    return {"doc_id": doc_id, "doc_name": doc_name, "chunks_stored": len(chunks_text)}


def ingest_url(url: str, doc_name: str | None = None, doc_set: str | None = None, max_pages: int = 25) -> dict:
    pages_text = _crawl_url(url, max_pages=max_pages)
    full_text = "\n\n".join(pages_text)
    chunks_text = _chunk_text(full_text)
    name = doc_name or _domain_label(url)
    doc_id = _store(doc_name=name, source_url=url, doc_set=doc_set, chunks_text=chunks_text)
    return {"doc_id": doc_id, "doc_name": name, "chunks_stored": len(chunks_text)}


# ── Private helpers ──────────────────────────────────────────────────────────

def _extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def _crawl_url(start_url: str, max_pages: int = 25) -> list[str]:
    """BFS crawl within the same domain, up to max_pages pages."""
    base = _base_url(start_url)
    visited: set[str] = set()
    queue = [start_url]
    pages_text: list[str] = []

    with httpx.Client(timeout=15, follow_redirects=True) as client:
        while queue and len(visited) < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            try:
                resp = client.get(url)
                resp.raise_for_status()
            except Exception:
                continue
            visited.add(url)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove nav, header, footer noise
            for tag in soup(["nav", "header", "footer", "script", "style"]):
                tag.decompose()

            text = soup.get_text(separator="\n")
            text = _clean_text(text)
            if text:
                pages_text.append(text)

            # Collect same-domain links
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full = urljoin(url, href).split("#")[0]
                if full.startswith(base) and full not in visited:
                    queue.append(full)

    return pages_text


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks on sentence boundaries."""
    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text.strip())

    # Split into sentences (rough)
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= CHUNK_CHARS:
            current += (" " if current else "") + sentence
        else:
            if current:
                chunks.append(current.strip())
            # Start new chunk with overlap from end of previous
            overlap = current[-OVERLAP_CHARS:] if len(current) > OVERLAP_CHARS else current
            current = overlap + " " + sentence if overlap else sentence

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) > 50]  # drop trivially short chunks


def _store(doc_name: str, source_url: str | None, doc_set: str | None, chunks_text: list[str]) -> int:
    doc_id = insert_document(doc_name=doc_name, source_url=source_url, doc_set=doc_set)
    embeddings = embed_texts(chunks_text)
    chunks = [
        {"chunk_index": i, "text": t, "embedding": e}
        for i, (t, e) in enumerate(zip(chunks_text, embeddings))
    ]
    insert_chunks(doc_id, chunks)
    return doc_id


def _base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _domain_label(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def _clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [l for l in lines if l]
    return "\n".join(lines)
