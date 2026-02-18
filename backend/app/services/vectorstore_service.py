import json
from typing import List, Dict

from app.db import SessionLocal
from app.models import Document, AIRequest, AIResult, DocumentIn
from app.utils.ollama_client import generate_answer
from app.vectorstore import PGVectorIngestor, PGVectorRetriever


def ingest_documents(tenant_id: str, documents: List[DocumentIn]) -> List[int]:
    db = SessionLocal()
    
    print(f"Ingesting {len(documents)} documents for tenant {tenant_id}")
    
    try:
        ingestor = PGVectorIngestor(db=db)
        doc_ids: List[int] = []
        for doc in documents:
            doc_row = Document(tenant_id=tenant_id, source=doc.source, content=doc.content)
            db.add(doc_row)
            db.commit()
            db.refresh(doc_row)

            chunks = ingestor.split_documents([doc.content])
            ingestor.embed_and_store(chunks, tenant_id, doc.source, doc_row.id)
            doc_ids.append(doc_row.id)
        return doc_ids
    finally:
        db.close()


def query_knowledge(tenant_id: str, question: str, k: int = 5) -> Dict:
    db = SessionLocal()
    try:
        retriever = PGVectorRetriever(db=db, k=k)
        contexts = retriever.search(tenant_id=tenant_id, query=question)
        chunks = [c.get("chunk", "") for c in contexts if c.get("chunk")]

        answer = generate_answer(question, chunks)
        citations = [f"doc:{c.get('doc_id')}:{c.get('source')}" for c in contexts]

        req = AIRequest(tenant_id=tenant_id, question=question)
        db.add(req)
        db.commit()
        db.refresh(req)

        result = AIResult(
            request_id=req.id,
            tenant_id=tenant_id,
            answer=answer,
            citations=json.dumps(citations),
        )
        db.add(result)
        db.commit()

        return {"answer": answer, "citations": citations}
    finally:
        db.close()
