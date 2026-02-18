from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Tenant, Document, TenantCreate, IngestRequest, QueryRequest, QueryResponse
from app.vectorstore import PGVectorIngestor
from app.memory import cache_get, cache_set
from app.config.settings import settings
from app.routers.knowledge_service import answer_question

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.post("/tenants")
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    existing = db.query(Tenant).filter(Tenant.id == payload.id).first()
    if existing:
        return {"id": existing.id, "name": existing.name}
    tenant = Tenant(id=payload.id, name=payload.name)
    db.add(tenant)
    db.commit()
    return {"id": tenant.id, "name": tenant.name}


@router.post("/ingest")
def ingest(payload: IngestRequest, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    doc_ids = []
    ingestor = PGVectorIngestor(db=db)
    for doc in payload.documents:
        doc_row = Document(tenant_id=payload.tenant_id, source=doc.source, content=doc.content)
        db.add(doc_row)
        db.commit()
        db.refresh(doc_row)
        chunks = ingestor.split_documents([doc.content])
        ingestor.embed_and_store(chunks, payload.tenant_id, doc.source, doc_row.id)
        doc_ids.append(doc_row.id)

    return {"ingested": len(doc_ids), "document_ids": doc_ids}


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    cache_key = f"q:{payload.tenant_id}:{payload.question}"
    cached = cache_get(cache_key)
    if cached:
        return QueryResponse(**cached, cached=True)

    result = answer_question(db, payload.tenant_id, payload.question)
    response = {"answer": result["answer"], "citations": result["citations"], "cached": False}
    cache_set(cache_key, response, settings.cache_ttl_seconds)
    return QueryResponse(**response)
