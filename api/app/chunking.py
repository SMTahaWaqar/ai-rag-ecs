from typing import List

def chunk_text(text: str, size: int = 600, overlap: int = 100) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks: List[str] = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks
