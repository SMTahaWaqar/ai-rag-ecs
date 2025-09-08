import logging
from fastapi import FastAPI
from pydantic import BaseModel
from .logging_middleware import RequestLogginMiddleware
from .db_health import router as db_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("rag")

app = FastAPI(title="Docs Q&A (RAG) API", version="0.1.0")
app.add_middleware(RequestLogginMiddleware)
app.include_router(db_router)

class AskRequest (BaseModel):
    question: str

@app.get("/health")
def health():
    return { "status": "ok" }

@app.post("/ask")
def ask(req: AskRequest):
    return { "answer": "coming soon", "question": req.question }