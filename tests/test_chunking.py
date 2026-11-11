import pytest

from app.services.chunking import chunk_text, split_into_sentences


def test_chunk_text_with_default_parameters():
    text = " ".join(f"word{i}" for i in range(250))

    chunks = chunk_text(text)

    assert len(chunks) == 3
    assert len(chunks[0].split()) == 100
    assert len(chunks[1].split()) == 100
    assert len(chunks[2].split()) == 90


def test_chunk_text_overlap():
    text = " ".join(f"word{i}" for i in range(150))

    chunks = chunk_text(
        text,
        chunk_size_words=100,
        overlap_words=20
    )

    first_chunk_words = chunks[0].split()
    second_chunk_words = chunks[1].split()

    assert first_chunk_words[-20:] == second_chunk_words[:20]


def test_chunk_text_without_overlap():
    text = " ".join(f"word{i}" for i in range(150))

    chunks = chunk_text(
        text,
        chunk_size_words=100,
        overlap_words=0
    )

    assert len(chunks) == 2
    assert chunks[0].split()[-1] == "word99"
    assert chunks[1].split()[0] == "word100"


def test_chunk_text_empty_input():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_rejects_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("Hello world", chunk_size_words=0)


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            "Hello world",
            chunk_size_words=100,
            overlap_words=100
        )


def test_split_into_sentences():
    text = "Python is useful. SQL is important. Data is valuable."

    sentences = split_into_sentences(text)

    assert sentences == [
        "Python is useful.",
        "SQL is important.",
        "Data is valuable."
    ]


def test_split_into_sentences_with_paragraphs():
    text = (
        "First paragraph sentence one. "
        "First paragraph sentence two.\n\n"
        "Second paragraph sentence one."
    )

    sentences = split_into_sentences(text)

    assert len(sentences) == 3


def test_chunk_text_preserves_sentence_boundaries():
    text = (
        "Python is a programming language. "
        "Pandas is used for data processing. "
        "PostgreSQL is a relational database."
    )

    chunks = chunk_text(
        text,
        chunk_size_words=8,
        overlap_words=0
    )

    assert chunks == [
        "Python is a programming language.",
        "Pandas is used for data processing.",
        "PostgreSQL is a relational database."
    ]


def test_chunk_text_splits_long_sentence():
    text = " ".join(f"word{i}" for i in range(150)) + "."

    chunks = chunk_text(
        text,
        chunk_size_words=100,
        overlap_words=0
    )

    assert len(chunks) == 2
    assert len(chunks[0].split()) == 100
    assert len(chunks[1].split()) == 50


def test_chunk_text_overlap_preserves_sentences():
    text = (
        "One two three four five. "
        "Six seven eight nine ten. "
        "Eleven twelve thirteen fourteen fifteen."
    )

    chunks = chunk_text(
        text,
        chunk_size_words=10,
        overlap_words=5
    )

    assert chunks[0] == "One two three four five. Six seven eight nine ten."
    assert chunks[1] == "Six seven eight nine ten. Eleven twelve thirteen fourteen fifteen."


def test_chunk_text_never_exceeds_maximum_size():
    text = " ".join(
        f"word{i}." if (i + 1) % 10 == 0 else f"word{i}"
        for i in range(350)
    )

    chunk_size = 100

    chunks = chunk_text(
        text,
        chunk_size_words=chunk_size,
        overlap_words=20
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk.split()) <= chunk_size