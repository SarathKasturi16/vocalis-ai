"""Build the Q2 knowledge base from raw data files."""

from pathlib import Path
import json

from ingestion.cleaner import clean_text, normalize_terms
from ingestion.pii_detector import redact
from ingestion.deduplicator import remove_duplicates
from ingestion.chunker import chunk_text
from ingestion.pdf_loader import load_pdf
from ingestion.table_loader import load_table
from retrieval.vector_store import reset, add

RAW = Path("data/raw")
OUT = Path("data/processed")


def load_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix in {".csv", ".xlsx", ".xls"}:
        return load_table(path)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported file: {path}")


def classify(path: Path, title: str, content: str) -> str:
    """Auto-classify a chunk into a product/policy taxonomy category."""
    s = f"{path.name} {title} {content}".lower()

    if "objection" in path.name.lower():
        return "objection"
    if "document" in path.name.lower():
        return "documentation"
    if any(t in s for t in ["interest rate", "processing fee", "prepayment", "quotation"]):
        return "pricing"
    if any(t in s for t in ["minimum age", "business exist", "minimum turnover",
                            "eligibility", "eligible applicants"]):
        return "qualification"
    if "faq" in path.name.lower():
        return "faq"
    if any(t in s for t in ["loan purpose", "inventory", "working capital"]):
        return "product_policy"
    return "product_policy"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []

    for path in sorted(RAW.rglob("*")):
        if not path.is_file():
            continue
        try:
            raw = load_file(path)
            cleaned = normalize_terms(clean_text(raw))
        except Exception as exc:
            print(f"[WARN] {path}: {exc}")
            continue

        if not cleaned:
            continue

        for i, part in enumerate(chunk_text(cleaned)):
            safe_text, has_pii = redact(part["content"])
            records.append({
                "record_id": f"kb_{path.stem}_{i+1:03d}",
                "title": part["title"],
                "content": safe_text,
                "category": classify(path, part["title"], safe_text),
                "source": str(path).replace("\\", "/"),
                "version": "1.0",
                "pii": has_pii,
                "effective_date": "2026-08-01",
            })

    records = remove_duplicates(records)

    # Save structured KB records
    (OUT / "kb_records.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )

    # Index into ChromaDB
    reset()
    add(records)

    print(f"Indexed {len(records)} records into ChromaDB.")


if __name__ == "__main__":
    main()
