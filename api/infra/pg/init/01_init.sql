CREATE EXTENSION IF NOT EXISTS vector;

-- We'll start with 384-dim embeddings (e.g., MiniLM/e5-small).
-- Change later if we pick a different model.
CREATE TABLE IF NOT EXISTS docs (
    id BIGSERIAL PRIMARY KEY,
    chunk TEXT NOT NULL,
    embedding VECTOR(384) -- <-- dimension matters
)