from .db import connect

def ensure_schema() -> None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS docs (
              id BIGSERIAL PRIMARY KEY,
              chunk TEXT NOT NULL,
              embedding VECTOR(384)
            );
        """)
        cur.execute("ALTER TABLE docs ADD COLUMN IF NOT EXISTS doc_id TEXT DEFAULT 'default';")
        conn.commit()
