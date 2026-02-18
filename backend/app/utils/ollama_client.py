import hashlib
from typing import List
import requests

from app.config.settings import settings


REFUSAL = "I don't have enough context to answer that question based on the available documents."


def embed_text(text_value: str) -> List[float]:
    payload = {"model": settings.ollama_embed_model, "prompt": text_value}
    try:
        resp = requests.post(f"{settings.ollama_url}/api/embeddings", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        embedding = data.get("embedding")
        if embedding and isinstance(embedding, list):
            if len(embedding) != settings.embedding_dim:
                raise ValueError("Embedding dimension mismatch")
            return embedding
    except Exception:
        return _fallback_embed(text_value)
    return _fallback_embed(text_value)


def _fallback_embed(text_value: str) -> List[float]:
    digest = hashlib.sha256(text_value.encode("utf-8")).digest()
    needed = settings.embedding_dim
    data = (digest * (needed // len(digest) + 1))[:needed]
    return [((b / 255.0) * 2.0 - 1.0) for b in data]


def generate_answer(question: str, contexts: List[str]) -> str:
    if not contexts:
        return REFUSAL

    top_chunks = "\n\n".join(contexts[:5])
    prompt = (
        "You are an internal knowledge assistant. Use only the provided context. "
        "If the answer is not in the context, respond with: "
        f"\"{REFUSAL}\". Do not guess.\n\n"
        f"Question: {question}\n\n"
        f"Context:\n{top_chunks}\n\n"
        "Answer in a concise paragraph."
    )

    payload = {"model": settings.ollama_model, "prompt": prompt, "stream": False}
    try:
        resp = requests.post(f"{settings.ollama_url}/api/generate", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip() or REFUSAL
    except Exception:
        return REFUSAL
