"""
Hybrid retrieval: BGE vector + TF-IDF lexical + keyword overlap → BGE reranker.
"""

from typing import Any

from embeddings.embedder import encode
from retrieval.vector_store import collection
from retrieval.reranker import rerank
from app_config import config


def _normalize_score(score: float) -> float:
    if score is None:
        return 0.0
    return max(0.0, min(1.0, float(score)))


def _keyword_overlap(query: str, text: str) -> float:
    """Simple keyword overlap for exact business terms."""
    query_words = {w.lower() for w in query.split() if len(w) > 2}
    text_words = {w.lower() for w in text.split() if len(w) > 2}
    if not query_words:
        return 0.0
    return len(query_words & text_words) / len(query_words)


def _vector_search(query: str, top_k: int = 8) -> list[dict[str, Any]]:
    """Dense semantic retrieval using BGE embeddings + ChromaDB."""
    query_embedding = encode([query])[0]

    result = collection().query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]

    results = []
    for doc, meta, dist in zip(docs, metas, dists):
        meta = meta or {}
        rid = meta.get("record_id")
        if not rid:
            continue
        results.append({
            "record_id": rid,
            "content": doc,
            "metadata": meta,
            "vector_score": 1.0 / (1.0 + float(dist)),
            "tfidf_score": None,
        })
    return results


def _lexical_search(query: str, top_k: int = 8) -> list[dict[str, Any]]:
    """TF-IDF lexical retrieval from the stored kb_records.json."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import json
        from pathlib import Path

        path = Path("data/processed/kb_records.json")
        if not path.exists():
            return []

        records = json.loads(path.read_text(encoding="utf-8"))
        documents = [r["content"] for r in records]

        vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
        matrix = vectorizer.fit_transform(documents)
        query_vec = vectorizer.transform([query])
        scores = (matrix @ query_vec.T).toarray().ravel()

        ranked = scores.argsort()[::-1][:top_k]
        results = []
        for idx in ranked:
            s = float(scores[idx])
            if s <= 0:
                continue
            r = records[idx]
            results.append({
                "record_id": r["record_id"],
                "content": r["content"],
                "metadata": r,
                "vector_score": None,
                "tfidf_score": s,
            })
        return results
    except Exception:
        return []


def retrieve(query: str, top_k: int = 8) -> dict[str, Any]:
    """
    Hybrid retrieval pipeline:
      1. BGE vector search
      2. TF-IDF lexical search
      3. Merge + keyword overlap + hybrid pre-rank
      4. BGE cross-encoder rerank
      5. Grounding threshold check
    Returns {"grounded": bool, "results": list[dict]}
    """
    vector_results = _vector_search(query, top_k=top_k)
    lexical_results = _lexical_search(query, top_k=top_k)

    # Merge by record_id
    merged: dict[str, dict] = {}
    for item in vector_results:
        merged[item["record_id"]] = {**item}
    for item in lexical_results:
        rid = item["record_id"]
        if rid not in merged:
            merged[rid] = {**item}
        elif item["tfidf_score"] is not None:
            merged[rid]["tfidf_score"] = item["tfidf_score"]

    candidates = list(merged.values())

    # Keyword overlap
    for c in candidates:
        c["keyword_score"] = _keyword_overlap(query, c["content"])

    # Hybrid pre-ranking
    for c in candidates:
        c["hybrid_score"] = (
            0.50 * _normalize_score(c.get("vector_score"))
            + 0.30 * _normalize_score(c.get("tfidf_score"))
            + 0.20 * _normalize_score(c.get("keyword_score"))
        )

    candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
    candidates = candidates[:top_k]

    if not candidates:
        return {"grounded": False, "results": []}

    # BGE reranking
    candidates = rerank(query, candidates)

    grounded = bool(
        candidates and candidates[0]["rerank_score"] >= config.min_rerank_score
    )

    return {"grounded": grounded, "results": candidates}
