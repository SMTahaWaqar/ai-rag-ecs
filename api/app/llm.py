import os, json
from typing import Optional

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "").lower()
LLM_MODEL = os.environ.get("LLM_MODEL", "phi3:mini")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

def _build_prompt(question: str, context: str) -> str:
    return (
        "You are a helpful assistant. Answer using ONLY the provided context.\n"
        "If the answer isn't clearly in the context, say you don't know.\n\n"
        f"Question: {question}\n\n"
        f"Context: {context}\n\n"
        "Answer (concise, with no new facts):"
    )

def call_llm(question: str, context: str) -> Optional[str]:
    """
    Returns model answer string or None if provider not configured or call fails.
    """

    prompt = _build_prompt(question, context)

    if not LLM_PROVIDER:
        return None

    try:
        if LLM_PROVIDER == "ollama":
            try:
                import os, requests
            except ModuleNotFoundError:
                return None
            
            num_ctx = int(os.environ.get("OLLAMA_NUM_CTX", "1024"))    # smaller = less RAM & faster
            num_thread = int(os.environ.get("OLLAMA_NUM_THREAD", max(1, (os.cpu_count() or 4) // 2)))
            keep_alive = os.environ.get("OLLAMA_KEEP_ALIVE", "10m")    # keep model in RAM for 10min idle
            r = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": LLM_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_ctx": num_ctx,
                        "num_thread": num_thread,
                        # small sampling tweaks help stability/consistency; not required for speed
                        "temperature": 0.1
                    },
                    "keep_alive": keep_alive
                },
                timeout=120,
            )
            if not r.ok:
                return None
            text = r.json().get("response", "")
            return text.strip() if isinstance(text, str) else None
    except Exception as e:
        return None
    
    return ModuleNotFoundError