from pathlib import Path

def load_pdf(path: Path) -> str:
    # Unstructured is the primary parser.
    from unstructured.partition.pdf import partition_pdf
    elements = partition_pdf(filename=str(path))
    return "\n".join(str(e) for e in elements if str(e).strip())
