import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    embedding_model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    reranker_model = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-TinyBERT-L-2-v2")
    chroma_path = os.getenv("CHROMA_PATH", "./data/processed/chroma")
    retrieval_top_k = int(os.getenv("RETRIEVAL_TOP_K", "8"))
    min_rerank_score = float(os.getenv("MIN_RERANK_SCORE", "0.20"))

config = Config()
