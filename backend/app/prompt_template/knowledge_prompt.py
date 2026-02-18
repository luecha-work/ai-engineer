from app.utils.ollama_client import REFUSAL


def get_knowledge_prompt_system() -> str:
    return (
        "You are an internal knowledge assistant. Use only the provided context. "
        f"If the answer is not in the context, respond with: \"{REFUSAL}\". "
        "Do not guess."
    )
