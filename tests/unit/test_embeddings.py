"""Unit tests for embedding generation — fastembed mocked."""
import pytest
from unittest.mock import patch, MagicMock
import numpy as np


def _make_fake_embedding(dim=384):
    return np.random.rand(dim).tolist()


@patch("backend.embeddings._get_fastembed_model")
def test_embed_texts_returns_list(mock_model_fn):
    fake_model = MagicMock()
    fake_model.embed.return_value = [np.array(_make_fake_embedding())]
    mock_model_fn.return_value = fake_model

    from backend.embeddings import embed_texts
    result = embed_texts(["hello world"])

    assert isinstance(result, list)
    assert len(result) == 1
    assert len(result[0]) == 384


@patch("backend.embeddings._get_fastembed_model")
def test_embed_texts_batch(mock_model_fn):
    fake_model = MagicMock()
    fake_model.embed.return_value = [np.array(_make_fake_embedding()) for _ in range(3)]
    mock_model_fn.return_value = fake_model

    from backend.embeddings import embed_texts
    result = embed_texts(["a", "b", "c"])
    assert len(result) == 3


@patch("backend.embeddings._get_fastembed_model")
def test_embed_query_returns_flat_list(mock_model_fn):
    fake_model = MagicMock()
    fake_model.embed.return_value = [np.array(_make_fake_embedding())]
    mock_model_fn.return_value = fake_model

    from backend.embeddings import embed_query
    result = embed_query("test query")
    assert isinstance(result, list)
    assert len(result) == 384
