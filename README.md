# Docs Q&A (RAG) — API
Tiny FastAPI service for a RAG demo. Today: `/health`, `/ask` placeholder.
Next: pgvector + retrieval + LLM provider toggle.

## Dev quickstart
```bash
cd api
python -m venv .venv && . .venv/Scripts/activate    # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
