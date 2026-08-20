"""Voice-agent tool functions called by Vapi via the FastAPI backend."""

import sqlite3
from pathlib import Path
from retrieval.retriever import retrieve
from generation.rag import answer

DB = Path("data/processed/app.db")


def search_knowledge(question: str) -> dict:
    """Retrieve grounded answer from the knowledge base."""
    result = retrieve(question)
    if not result["grounded"]:
        return {
            "grounded": False,
            "answer": (
                "I don't have enough verified information to answer that "
                "accurately. I can connect you with a human representative."
            ),
            "sources": [],
        }
    generated = answer(question, result["results"])
    generated["grounded"] = True
    return generated


def create_lead(qualification: dict) -> dict:
    """Store qualified lead in SQLite (business action)."""
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            business_name TEXT,
            business_type TEXT,
            years_in_business REAL,
            annual_turnover REAL,
            requested_amount REAL,
            loan_purpose TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    fields = [
        "name", "phone", "business_name", "business_type",
        "years_in_business", "annual_turnover",
        "requested_amount", "loan_purpose",
    ]
    cur = conn.execute(
        """
        INSERT INTO leads
        (name, phone, business_name, business_type, years_in_business,
         annual_turnover, requested_amount, loan_purpose)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        tuple(qualification.get(k) for k in fields),
    )
    conn.commit()
    lead_id = cur.lastrowid
    conn.close()
    return {"success": True, "lead_id": lead_id}
