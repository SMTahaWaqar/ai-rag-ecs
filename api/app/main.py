import logging
from fastapi import FastAPI
from pydantic import BaseModel
from .logging_middleware import RequestLogginMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("rag")

app = FastAPI(title="Docs Q&A (RAG) API", version="0.1.0")
app.add_middleware(RequestLogginMiddleware)

class AskRequest (BaseModel):
    question: str

@app.get("/health")
def health():
    return { "status": "ok" }

@app.post("/ask")
def ask(req: AskRequest):
    return { "answer": "coming soon", "question": req.question }