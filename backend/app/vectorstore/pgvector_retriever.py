from typing import Dict, List
from langchain_community.embeddings import OllamaEmbeddings
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.vectorstore.base_vector_retriever import BaseVectorRetriever


class PGVectorRetriever(BaseVectorRetriever):
    def __init__(self, db: Session, k: int = 5):
        self.db = db
        self.embeddings = OllamaEmbeddings(
            model=settings.ollama_embed_model,
            base_url=settings.ollama_url,
        )
        super().__init__(k=k)

    def _initialize(self):
        return None

    def search(self, tenant_id: str, query: str) -> List[Dict]:
        query_vec = self.embeddings.embed_query(query)
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
