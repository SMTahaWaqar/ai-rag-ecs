import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from .logging_middleware import RequestLogginMiddleware
from .db_health import router as db_router
from .ingest_search import router as rag_router
from .bootstrap import ensure_schema
from .ask import router as ask_router, warm_router
from .llm import call_llm

env_file = os.getenv("ENV_FILE")
if env_file:
    load_dotenv(env_file)
else:
    root = Path(__file__).resolve().parents[2]  # repo root
    for name in (".env.development", ".env"):
        f = root / name
        if f.exists():
            load_dotenv(f)
            break

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("rag")
ensure_schema()
app = FastAPI(title="Docs Q&A (RAG) API", version="0.1.0")
app.add_middleware(RequestLogginMiddleware)
app.include_router(db_router)
app.include_router(rag_router)
app.include_router(ask_router)
app.include_router(warm_router)

@app.on_event("startup")
def _startup():
    # optional best-effort warm
    try: call_llm("ping", "respond with 'ok' only")
    except: pass

class AskRequest (BaseModel):
    question: str

@app.get("/health")
def health():
    return { "status": "ok" }

@app.post("/ask")
def ask(req: AskRequest):
    return { "answer": "coming soon", "question": req.question }