import hashlib
import re

def fingerprint(text: str) -> str:
    normalized = re.sub(r"\W+", " ", text.lower()).strip()
    return hashlib.sha256(normalized.encode()).hexdigest()

def remove_duplicates(records):
    seen = set()
    output = []
    for record in records:
        fp = fingerprint(record["content"])
        if fp in seen:
            continue
        seen.add(fp)
        output.append(record)
    return output
