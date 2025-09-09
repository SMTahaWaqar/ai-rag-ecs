import os
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from .db import connect
from .embeddings import embed_text, to_vector_sql, EMBED_DIM
from .llm import call_llm

router = APIRouter()
warm_router = APIRouter()
MAX_CONTENT_CHARS = int(os.environ.get("MAX_CONTENT_CHARS", "2000"))

@warm_router.get("/warmup")
def warmup():
    _ = call_llm("ping", "respond with 'ok' only")
    return {"warmed": True}

class AskRequest(BaseModel):
    question: str
    k: int = 2

class Citation(BaseModel):
    id: int
    distance: float
    chunk: str

class AskResp(BaseModel):
    answer: str
    citations: List[Citation]

@router.post("/ask", response_model=AskResp)
def ask(req: AskRequest):
    # 1: Rerieve
    qvec = embed_text(req.question)
    qvec_sql = to_vector_sql(qvec)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, chunk, (embedding <-> %s::vector) AS distance
            FROM docs
            ORDER BY embedding <-> %s::vector
            LIMIT %s
            """,
            (qvec_sql, qvec_sql, req.k),
        )
        rows = cur.fetchall()
    hits = [Citation(id=r[0], chunk=r[1], distance=float(r[2])) for r in rows]

    # 2) build context (truncate to avoid massive prompts)
    # keep chunks sorted by distance ascending
    context = ""
    for h in hits:
        if len(context) + len(h.chunk) + 50 > MAX_CONTENT_CHARS:
            break
        context += f"- {h.chunk}\n"

    # 3) try LLM (if configured), else extractive fallback
    answer = call_llm(req.question, context)
    if not isinstance(answer, str) or not answer.strip():
        if hits:
            answer = f"(extractive) Closest match:\n{hits[0].chunk}"
        else:
            answer = "I don't have enough context to answer that."
    return AskResp(answer=answer, citations=hits)
