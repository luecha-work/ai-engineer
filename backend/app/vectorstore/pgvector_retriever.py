from typing import List, Dict
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.vectorstore.base_vector_retriever import BaseVectorRetriever
from app.utils.ollama_client import embed_text


class PGVectorRetriever(BaseVectorRetriever):
    def __init__(self, db: Session, k: int = 5):
        self.db = db
        super().__init__(k=k)

    def _initialize(self):
        return None

    def search(self, tenant_id: str, query: str) -> List[Dict]:
        query_vec = embed_text(query)
        stmt = text(
            """
            SELECT id, doc_id, source, chunk
            FROM document_chunks
            WHERE tenant_id = :tenant_id
            ORDER BY embedding <-> :query_vec
            LIMIT :limit
            """
        )
        rows = (
            self.db.execute(
                stmt,
                {"tenant_id": tenant_id, "query_vec": query_vec, "limit": self.k},
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]
