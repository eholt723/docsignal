"""
Q&A pipeline: retrieve top-k chunks via similarity search, synthesize answer
with Groq (llama-3.1-8b-instant), return answer + cited sources.
"""
import os
from openai import OpenAI
from backend.embeddings import embed_query
from backend.database import similarity_search, log_query
from backend.models import Citation

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)
LLM_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """\
You are a precise documentation assistant. Answer the user's question using ONLY the provided context passages.
Be concise and direct. Synthesize the answer from what is present in the context — do not preface with phrases like \
"the context does not explicitly state" or "based on the provided examples". Just answer.
Only if the context contains genuinely no relevant information should you say you cannot answer.
Do not make up information or draw from outside knowledge.
"""


def ask(question: str, doc_set: str | None, top_k: int = 5) -> dict:
    query_vec = embed_query(question)
    chunks = similarity_search(query_vec, doc_set=doc_set, top_k=top_k)

    if not chunks:
        log_query(question, doc_set, None)
        return {
            "question": question,
            "answer": "No relevant documentation found. Please ingest a document first.",
            "citations": [],
        }

    context = _build_context(chunks)
    answer = _synthesize(question, context)

    top_similarity = chunks[0]["similarity"] if chunks else None
    log_query(question, doc_set, top_similarity)

    citations = [
        Citation(
            doc_name=c["doc_name"],
            source_url=c["source_url"],
            text=c["text"],
            similarity=round(c["similarity"], 4),
        )
        for c in chunks
    ]

    return {"question": question, "answer": answer, "citations": citations}


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[{i}] Source: {c['doc_name']}\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def _synthesize(question: str, context: str) -> str:
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
        max_tokens=800,
    )
    return response.choices[0].message.content.strip()
