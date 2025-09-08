import os
import psycopg
from fastapi import APIRouter

router = APIRouter()

def _dsn() -> str:
    return os.environ.get("DATABASE_URL", "postgresql://rag:rag@localhost:5432/rag")

@router.get("/db/health")
def db_health():
    try:
        with psycopg.connect(_dsn()) as conn:
            with conn.cursor() as cur:
                cur.execute("select 1")
                cur.fetchone()
        return { "db": "ok" }
    except Exception as e:
        return { "db": "error", "detail": str(e) }