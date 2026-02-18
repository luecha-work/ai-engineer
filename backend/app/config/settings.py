from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_name: str = "internal-knowledge-assistant"
    database_url: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/ai_assistant"
    redis_url: str = "redis://redis:6379/0"
    embedding_dim: int = 768
    cache_ttl_seconds: int = 300

    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "qwen3"
    ollama_embed_model: str = "qwen3-embedding"


settings = Settings()
