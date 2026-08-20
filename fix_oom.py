import os

# 1. Update app_config.py to use a tiny reranker
with open("app_config.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('"BAAI/bge-reranker-base"', '"cross-encoder/ms-marco-TinyBERT-L-2-v2"')
with open("app_config.py", "w", encoding="utf-8") as f:
    f.write(c)


# 2. Update requirements.txt to use CPU PyTorch
with open("requirements.txt", "r", encoding="utf-8") as f:
    reqs = f.read()

if "--extra-index-url" not in reqs:
    new_reqs = "--extra-index-url https://download.pytorch.org/whl/cpu\ntorch==2.2.2+cpu\n" + reqs
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(new_reqs)


# 3. Add memory limits to api/main.py
with open("api/main.py", "r", encoding="utf-8") as f:
    m = f.read()

if "OMP_NUM_THREADS" not in m:
    header = """import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
"""
    # Insert right after the first line (or at the top)
    m = header + m
    with open("api/main.py", "w", encoding="utf-8") as f:
        f.write(m)

