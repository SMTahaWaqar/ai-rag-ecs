import os
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from .db import connect
from .embeddings import embed_text, to_vector_sql, EMBED_DIM
from .chunking import chunk_text

router = APIRouter()
EMBED_DIM = int(os.environ.get("EMBEDDING_DIM", "384"))

class IngestReq(BaseModel):
    text: str
    chunk_size: int = 600
    overlap: int = 100
    doc_id: Optional[str] = "default"

class IngestResp(BaseModel):
    chunks_saved: int

@router.post("/ingest", response_model=IngestResp)
def ingest(req: IngestReq):
    chunks = chunk_text(req.text, req.chunk_size, req.overlap)
    if not chunks:
        return IngestResp(chunks_saved=0)
    
    inserted = 0
    with connect() as conn:
        with conn.cursor() as cur:
            for ch in chunks:
                vec = embed_text(ch)
                vec_sql = to_vector_sql(vec)
                cur.execute(
                    """
                    INSERT INTO docs (doc_id, chunk, embedding)
                    SELECT %s, %s, %s::vector
                    WHERE NOT EXISTS (
                        SELECT 1 FROM docs WHERE doc_id = %s AND chunk = %s
                    )
                """,
                (req.doc_id, ch, vec_sql, req.doc_id, ch),
            )
            inserted += cur.rowcount
        conn.commit()
    return IngestResp(chunks_saved=inserted)

class SearchReq(BaseModel):
    query: str
    k: int = 3

class SearchHit(BaseModel):
    id: int
    distance: float
    chunk: str

class SearchResp(BaseModel):
    hits: List[SearchHit]

@router.post("/search", response_model=SearchResp)
def search(req: SearchReq):
    qvec = embed_text(req.query)
    qvec_sql = to_vector_sql(qvec)
    with connect() as conn:
        with conn.cursor() as cur:
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
    hits = [SearchHit(id=r[0], chunk=r[1], distance=float(r[2])) for r in rows]
    return SearchResp(hits=hits)