from sqlalchemy.orm import Session
from app.vectorstore import PGVectorRetriever


def get_knowledge_context(db: Session, tenant_id: str, query: str, k: int = 5):
    retriever = PGVectorRetriever(db=db, k=k)
    return retriever.search(tenant_id=tenant_id, query=query)
