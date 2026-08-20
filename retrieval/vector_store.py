"""ChromaDB vector store for the knowledge base."""

from pathlib import Path
import chromadb
from embeddings.embedder import encode
from app_config import config

COLLECTION = "business_loan_kb"


def client():
    Path(config.chroma_path).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=config.chroma_path)


def collection():
    return client().get_or_create_collection(
        COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def reset():
    try:
        client().delete_collection(COLLECTION)
    except Exception:
        pass


def add(records):
    if not records:
        return
    collection().add(
        ids=[r["record_id"] for r in records],
        documents=[r["content"] for r in records],
        embeddings=encode([r["content"] for r in records]),
        metadatas=[
            {k: str(v) for k, v in r.items() if k != "content"}
            for r in records
        ],
    )
