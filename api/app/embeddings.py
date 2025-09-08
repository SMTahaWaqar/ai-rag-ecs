import os, hashlib
from typing import List

PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "fake").lower()
MODEL_NAME = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
EMBED_DIM = int(os.environ.get("EMBEDDING_DIM", "384"))

_model = None

def _init_model():
    global _model
    if PROVIDER == "fastemebed" and _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(model_name=MODEL_NAME)

def embed_text(text: str) -> List[float]:
    """"Return  an embedding  for a single string."""
    if PROVIDER == "fastembed":
        _init_model()
        vec = next(_model.embed([text])) # generator -> first vector
        return [float(x) for x in vec]
    # Fallback: deterministic fake embedding (kept for tests)
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vals: List[float] = []
    while len(vals) < EMBED_DIM:
        for b in h:
            vals.append((b / 255.0) * 2 - 1)  # map byte [0,255] to [-1,1]
            if len(vals) >= EMBED_DIM:
                break
    return vals

def to_vector_sql(vec: List[float]) -> str:
     # Format acceptable by pgvector: '[v1,v2,...]'
     return "[" + ",".join(f"{v: 6f}" for v in vec) + "]"