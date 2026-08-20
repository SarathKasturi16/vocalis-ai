from google import genai
from app_config import config

SYSTEM = """
You are a business-loan qualification assistant.

GROUNDING RULES:
- Answer business-policy questions only from VERIFIED CONTEXT.
- Never invent eligibility, rates, fees, approval guarantees, documents, or policies.
- If the context does not answer the question, say the information is unavailable.
- Do not treat general model knowledge as business policy.
- Keep answers short and natural for voice.
- If appropriate, offer human assistance.

Always include source IDs internally in the response object supplied by the application.
"""

def answer(question, results):
    if not results:
        return {
            "answer": "I don't have enough verified information to answer that accurately. I can connect you with a human representative.",
            "sources": []
        }

    context = "\n\n".join(
        f"[{r['metadata']['record_id']}] "
        f"{r['metadata'].get('source')} | "
        f"{r['metadata'].get('title')}\n{r['content']}"
        for r in results
    )

    if not config.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=config.gemini_api_key)
    prompt = f"""
{SYSTEM}

VERIFIED CONTEXT:
{context}

CUSTOMER QUESTION:
{question}

Return only the customer-facing answer. Do not mention the retrieval system.
"""

    response = client.models.generate_content(
        model=config.gemini_model,
        contents=prompt,
    )

    return {
        "answer": response.text.strip(),
        "sources": [
            {
                "record_id": r["metadata"]["record_id"],
                "source": r["metadata"].get("source"),
                "title": r["metadata"].get("title"),
                "score": r.get("rerank_score")
            }
            for r in results
        ]
    }
