import os
import numpy as np

EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "fastembed")
FASTEMBED_MODEL = "BAAI/bge-small-en-v1.5"
OPENAI_EMBED_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 384  # fastembed default; openai text-embedding-3-small is 1536

_fastembed_model = None


def _get_fastembed_model():
    global _fastembed_model
    if _fastembed_model is None:
        from fastembed import TextEmbedding
        _fastembed_model = TextEmbedding(model_name=FASTEMBED_MODEL)
    return _fastembed_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    if EMBEDDING_PROVIDER == "openai":
        return _embed_openai(texts)
    return _embed_fastembed(texts)


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def _embed_fastembed(texts: list[str]) -> list[list[float]]:
    model = _get_fastembed_model()
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]


def _embed_openai(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI
    client = OpenAI()
    response = client.embeddings.create(model=OPENAI_EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]
