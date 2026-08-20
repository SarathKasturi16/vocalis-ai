from pathlib import Path
import pandas as pd

def load_table(path: Path) -> str:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported table: {path}")
    return df.fillna("").to_csv(index=False)
