from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Docs Q&A (RAG) API", version="0.1.0")

class AskRequest (BaseModel):
    question: str

@app.get("/health")
def health():
    return { "status": "ok" }

@app.post("/ask")
def ask(req: AskRequest):
    return { "answer": "coming soon", "question": req.question }