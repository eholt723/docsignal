from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IngestRequest(BaseModel):
    url: str
    doc_name: Optional[str] = None


class IngestResponse(BaseModel):
    doc_id: int
    doc_name: str
    chunks_stored: int


class SearchRequest(BaseModel):
    query: str
    doc_set: Optional[str] = None
    top_k: int = 5


class ChunkResult(BaseModel):
    chunk_id: int
    doc_name: str
    source_url: Optional[str]
    text: str
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[ChunkResult]


class AskRequest(BaseModel):
    question: str
    doc_set: Optional[str] = None
    top_k: int = 5


class Citation(BaseModel):
    doc_name: str
    source_url: Optional[str]
    text: str
    similarity: float


class AskResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]


class AnalyticsOverview(BaseModel):
    total_queries: int
    total_chunks: int
    total_documents: int


class TopQuestion(BaseModel):
    query_text: str
    count: int


class TopSource(BaseModel):
    doc_name: str
    citation_count: int


class QueryVolume(BaseModel):
    date: str
    count: int


class SimilarityBucket(BaseModel):
    bucket: str
    count: int
