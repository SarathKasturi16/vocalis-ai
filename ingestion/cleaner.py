import re

def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    boilerplate = [
        r"(?im)^privacy policy\s*$",
        r"(?im)^terms and conditions\s*$",
        r"(?im)^cookie policy\s*$",
        r"(?im)^all rights reserved\.?\s*$",
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, "", text)

    lines = []
    previous = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line == previous:
            continue
        lines.append(line)
        previous = line
    return "\n".join(lines).strip()

def normalize_terms(text: str) -> str:
    replacements = {
        "SME loan": "business loan",
        "MSME loan": "business loan",
        "turn over": "turnover",
    }
    for old, new in replacements.items():
        text = re.sub(re.escape(old), new, text, flags=re.I)
    return text
