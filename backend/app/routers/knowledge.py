from fastapi import APIRouter, HTTPException

from app.db import SessionLocal
from app.models import (
    Tenant,
    TenantCreate,
    IngestRequest,
    QueryRequest,
    QueryResponse,
)
from app.memory import cache_get, cache_set
from app.config.settings import settings
from app.services.vectorstore_service import ingest_documents, query_knowledge

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.post("/tenants")
def create_tenant(payload: TenantCreate):
    db = SessionLocal()
    try:
        existing = db.query(Tenant).filter(Tenant.id == payload.id).first()
        if existing:
            return {"id": existing.id, "name": existing.name}
        tenant = Tenant(id=payload.id, name=payload.name)
        db.add(tenant)
        db.commit()
        return {"id": tenant.id, "name": tenant.name}
    finally:
        db.close()


@router.post("/ingest")
def ingest(payload: IngestRequest):
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
    finally:
        db.close()

    doc_ids = ingest_documents(payload.tenant_id, payload.documents)
    return {"ingested": len(doc_ids), "document_ids": doc_ids}


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest):
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
    finally:
        db.close()

    cache_key = f"q:{payload.tenant_id}:{payload.question}"
    cached = cache_get(cache_key)
    if cached:
        return QueryResponse(**cached, cached=True)

    result = query_knowledge(payload.tenant_id, payload.question, k=5)
    response = {"answer": result["answer"], "citations": result["citations"], "cached": False}
    cache_set(cache_key, response, settings.cache_ttl_seconds)
    return QueryResponse(**response)
