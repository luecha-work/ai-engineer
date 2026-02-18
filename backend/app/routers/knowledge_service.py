from typing import List, Dict
from sqlalchemy.orm import Session
import json

from app.models import AIRequest, AIResult
from app.vectorstore import PGVectorRetriever
from app.utils.ollama_client import generate_answer


def answer_question(db: Session, tenant_id: str, question: str) -> Dict:
    retriever = PGVectorRetriever(db=db, k=5)
    contexts = retriever.search(tenant_id=tenant_id, query=question)
    chunks: List[str] = [c.get("chunk", "") for c in contexts if c.get("chunk")]

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
