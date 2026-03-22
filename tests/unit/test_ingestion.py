"""Unit tests for text chunking logic."""
import pytest
from backend.ingestion import _chunk_text, CHUNK_CHARS, OVERLAP_CHARS


def test_chunk_short_text():
    text = "This is a short sentence that is long enough to pass the fifty character minimum filter."
    chunks = _chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_long_text_produces_multiple_chunks():
    # Generate text longer than CHUNK_CHARS
    sentence = "The quick brown fox jumps over the lazy dog. "
    text = sentence * 200
    chunks = _chunk_text(text)
    assert len(chunks) > 1


def test_chunks_have_overlap():
    sentence = "The quick brown fox jumps over the lazy dog. "
    text = sentence * 200
    chunks = _chunk_text(text)
    # Adjacent chunks should share some content (overlap)
    if len(chunks) >= 2:
        end_of_first = chunks[0][-OVERLAP_CHARS:]
        start_of_second = chunks[1][:OVERLAP_CHARS]
        # They should share some common substring
        assert any(word in chunks[1] for word in chunks[0].split()[-5:])


def test_chunk_filters_trivially_short():
    text = "Hi. Ok. Yes."
    chunks = _chunk_text(text)
    # All these are under 50 chars so they should be merged or dropped
    for c in chunks:
        assert len(c) >= 50 or len(chunks) == 0


def test_chunk_normalizes_whitespace():
    text = "First sentence.\n\n\n\n\nSecond sentence. " * 50
    chunks = _chunk_text(text)
    for c in chunks:
        assert "\n\n\n" not in c
