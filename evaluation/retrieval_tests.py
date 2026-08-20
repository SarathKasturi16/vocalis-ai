"""
Retrieval evaluation — 5 assessment queries.

Runs the full hybrid retrieval pipeline and reports per-query results
including record_id, source, scores, and verdict.
"""

import json
from pathlib import Path

from retrieval.retriever import retrieve


TEST_CASES = [
    {
        "question": "What is the minimum age for the business loan?",
        "expected_record": "kb_business_loan_policy_002",
        "expected_category": "qualification",
    },
    {
        "question": "Can I use the loan to buy inventory?",
        "expected_record": "kb_faq_007",
        "expected_category": "faq",
    },
    {
        "question": "What documents are typically required?",
        "expected_record": "kb_documentation_001",
        "expected_category": "documentation",
    },
    {
        "question": "Can you guarantee my interest rate?",
        "expected_record": "kb_pricing_and_fees_001",
        "expected_category": "pricing",
    },
    {
        "question": "What is the minimum annual turnover?",
        "expected_record": "kb_business_loan_policy_002",
        "expected_category": "qualification",
    },
]


def main():
    results = []
    correct = 0

    for test in TEST_CASES:
        question = test["question"]
        expected = test["expected_record"]
        expected_cat = test["expected_category"]

        response = retrieve(question, top_k=8)
        retrieved = response.get("results", [])

        if not retrieved:
            print(f"INCORRECT       | {question}")
            results.append({
                "question": question,
                "expected_record": expected,
                "retrieved_record": None,
                "verdict": "incorrect",
            })
            continue

        best = retrieved[0]
        rid = best["record_id"]
        cat = best["metadata"].get("category", "")

        # Exact match on record_id
        if rid == expected:
            verdict = "CORRECT"
            correct += 1
        # Category match counts as partially correct
        elif cat == expected_cat:
            verdict = "PARTIALLY CORRECT"
        else:
            verdict = "INCORRECT"

        print()
        print(f"{verdict:<20} | {question}")
        print(f"  record:        {rid}")
        print(f"  expected:      {expected}")
        print(f"  category:      {cat}")
        print(f"  source:        {best['metadata'].get('source')}")
        print(f"  rerank score:  {best.get('rerank_score')}")
        print(f"  chunk:         {best['content'][:120]}...")

        results.append({
            "question": question,
            "expected_record": expected,
            "retrieved_record": rid,
            "category": cat,
            "source": best["metadata"].get("source"),
            "title": best["metadata"].get("title"),
            "rerank_score": best.get("rerank_score"),
            "vector_score": best.get("vector_score"),
            "tfidf_score": best.get("tfidf_score"),
            "keyword_score": best.get("keyword_score"),
            "hybrid_score": best.get("hybrid_score"),
            "content": best["content"],
            "relevance_explanation": (
                f"Retrieved chunk from {cat} category. "
                f"Rerank score: {best.get('rerank_score', 0):.3f}. "
                f"Content addresses the query about: {question}"
            ),
            "verdict": verdict.lower(),
        })

    print()
    print(f"Retrieval evaluation: {correct}/{len(TEST_CASES)} exact match")

    out = Path("data/evaluation/retrieval_results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results saved to {out}")


if __name__ == "__main__":
    main()
