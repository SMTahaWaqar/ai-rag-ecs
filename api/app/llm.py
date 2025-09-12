import os
from typing import Optional

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "").lower()  # "openai" | "ollama"
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

SYSTEM_PROMPT = (
    "You are a precise RAG assistant. Use ONLY the provided context chunks.\n"
    'If the answer is not clearly present, say "I don\'t know". Keep answers concise.'
)

def _build_prompt(question: str, context: str) -> str:
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Question: {question}\n\n"
        "Context chunks (bullet list):\n"
        f"{context}\n\n"
        "Answer:"
    )

def call_llm(question: str, context: str) -> Optional[str]:
    """
    Return an answer string or None on any issue.
    Tries OpenAI if configured; if that fails and Ollama is configured, tries Ollama.
    """
    prompt = _build_prompt(question, context)

    if LLM_PROVIDER == "openai":
        try:
            from openai import OpenAI
            client = OpenAI()
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            text = resp.choices[0].message.content or ""
            return text.strip() or None
        except Exception:
            pass

    if LLM_PROVIDER == "ollama":
        try:
            import requests
        except ModuleNotFoundError:
            return None
        try:
            r = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": LLM_MODEL,
                    "prompt": prompt,
                    "system": SYSTEM_PROMPT,
                    "stream": False,
                    "options": {
                        "num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "768")),
                        "num_thread": int(os.environ.get("OLLAMA_NUM_THREAD", "4")),
                        "temperature": 0.1,
                    },
                    "keep_alive": os.environ.get("OLLAMA_KEEP_ALIVE", "10m"),
                },
                timeout=120,
            )
            if not r.ok:
                return None
            text = r.json().get("response", "")
            return text.strip() or None
        except Exception:
            return None

    return None
