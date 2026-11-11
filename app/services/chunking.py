import re


def split_into_sentences(text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text)

    sentences = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        paragraph_sentences = re.split(
            r"(?<=[.!?])\s+",
            paragraph
        )

        sentences.extend(
            sentence.strip()
            for sentence in paragraph_sentences
            if sentence.strip()
        )

    return sentences


def split_long_sentence(
    sentence: str,
    chunk_size_words: int,
    overlap_words: int = 0
) -> list[str]:
    words = sentence.split()

    step = chunk_size_words - overlap_words

    chunks = []

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size_words]

        chunks.append(" ".join(chunk_words))

        if start + chunk_size_words >= len(words):
            break

    return chunks


def chunk_text(
    text: str,
    chunk_size_words: int = 100,
    overlap_words: int = 20
) -> list[str]:

    if chunk_size_words <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap_words < 0:
        raise ValueError("Overlap cannot be negative.")

    if overlap_words >= chunk_size_words:
        raise ValueError("Overlap must be smaller than chunk size.")

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())

        if sentence_word_count > chunk_size_words:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0

            long_sentence_chunks = split_long_sentence(
                sentence,
                chunk_size_words,
                overlap_words
            )

            chunks.extend(long_sentence_chunks)
            continue

        if (
            current_word_count + sentence_word_count
            > chunk_size_words
            and current_chunk
        ):
            chunks.append(" ".join(current_chunk))

            overlap = []
            overlap_count = 0

            for previous_sentence in reversed(current_chunk):
                previous_word_count = len(previous_sentence.split())

                if overlap_count + previous_word_count > overlap_words:
                    break

                overlap.insert(0, previous_sentence)
                overlap_count += previous_word_count

            current_chunk = overlap
            current_word_count = overlap_count

        current_chunk.append(sentence)
        current_word_count += sentence_word_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
