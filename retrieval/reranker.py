from functools import lru_cache
from sentence_transformers import CrossEncoder
from app_config import config

@lru_cache(maxsize=1)
def model():
    return CrossEncoder(config.reranker_model)

def rerank(query, candidates):
    if not candidates:
        return []

    pairs = [(query, item["content"]) for item in candidates]
    scores = model().predict(pairs)

    output = []
    for item, score in zip(candidates, scores):
        item = dict(item)
        item["rerank_score"] = float(score)
        output.append(item)

    output.sort(key=lambda x: x["rerank_score"], reverse=True)
    return output
