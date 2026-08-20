from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app_config import config

@lru_cache(maxsize=1)
def model():
    return SentenceTransformer(config.embedding_model)

def encode(texts):
    return model().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    ).tolist()
