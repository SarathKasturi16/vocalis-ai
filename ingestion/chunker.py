"""Semantic chunking using sentence-embedding similarity."""

import re


def _normalize(text: str) -> str:
    """Collapse whitespace."""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_sentences(text: str) -> list[str]:
    """Split into sentences on .!? boundaries."""
    text = _normalize(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in parts if s.strip()]


def chunk_text(text: str, title: str = "") -> list[dict]:
    """
    Semantic chunking: group adjacent sentences whose embeddings
    are above a cosine-similarity threshold (0.5).  Falls back to
    fixed-window (3 sentences) if embeddings are unavailable.
    """
    sentences = _split_sentences(text)
    if not sentences:
        return []

    title = _normalize(title)

    try:
        from embeddings.embedder import encode
        from numpy import dot
        from numpy.linalg import norm

        embeddings = encode(sentences)

        chunks = []
        current = [sentences[0]]

        for i in range(1, len(sentences)):
            e1, e2 = embeddings[i - 1], embeddings[i]
            sim = dot(e1, e2) / (norm(e1) * norm(e2) + 1e-10)

            if sim > 0.5 and len(current) < 5:
                current.append(sentences[i])
            else:
                chunks.append({"title": title, "content": " ".join(current)})
                current = [sentences[i]]

        if current:
            chunks.append({"title": title, "content": " ".join(current)})

        return chunks

    except Exception as exc:
        print(f"[WARN] Semantic chunking unavailable, using fallback: {exc}")
        chunks = []
        step = 3
        for i in range(0, len(sentences), step):
            content = " ".join(sentences[i : i + step]).strip()
            if content:
                chunks.append({"title": title, "content": content})
        return chunks
