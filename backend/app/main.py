from fastapi import FastAPI
from sqlalchemy import text

from app.config.settings import settings
from app.db import Base, engine, SessionLocal
from app.routers.knowledge import router as knowledge_router


app = FastAPI(
    title="Internal Knowledge Assistant",
    description="Multi-tenant internal knowledge assistant API with pgvector + Ollama.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.commit()
        Base.metadata.create_all(bind=engine)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


app.include_router(knowledge_router)
