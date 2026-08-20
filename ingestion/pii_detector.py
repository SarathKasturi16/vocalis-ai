"""PII detection and redaction using regex + spaCy NER."""

import re
from functools import lru_cache

PHONE = re.compile(r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PAN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")


@lru_cache(maxsize=1)
def _load_spacy():
    """Load spaCy model once and cache it."""
    import spacy
    return spacy.load("en_core_web_sm")


def redact(text: str) -> tuple[str, bool]:
    """Return (redacted_text, had_pii)."""
    found = False
    for pattern in (PHONE, EMAIL, PAN):
        if pattern.search(text):
            found = True
            text = pattern.sub("[REDACTED]", text)

    try:
        nlp = _load_spacy()
        doc = nlp(text)
        replacements = [
            (ent.start_char, ent.end_char)
            for ent in doc.ents
            if ent.label_ in {"PERSON", "PHONE", "EMAIL"}
        ]
        for start, end in reversed(replacements):
            text = text[:start] + "[REDACTED]" + text[end:]
            found = True
    except Exception:
        pass

    return text, found
