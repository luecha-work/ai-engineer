from typing import List

from langchain_community.embeddings import OllamaEmbeddings
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models import Document, DocumentChunk
from app.utils.text_splitter import split_text
from app.vectorstore.base_ingestor import BaseKnowledgeIngestor


class PGVectorIngestor(BaseKnowledgeIngestor):
    def __init__(self, db: Session):
        self.db = db
        self.embeddings = OllamaEmbeddings(
            model=settings.ollama_embed_model,
            base_url=settings.ollama_url,
        )

    def load_documents(self, file_path: str) -> List[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            return [f.read()]

    def split_documents(self, documents: List[str]) -> List[str]:
        chunks: List[str] = []
        for doc in documents:
            chunks.extend(split_text(doc))
        return chunks

    def embed_and_store(
        self,
        documents: List[str],
        tenant_id: str,
        source: str,
        doc_id: int | None = None,
    ):
        if doc_id is None:
            doc_row = Document(tenant_id=tenant_id, source=source, content="\n".join(documents))
            self.db.add(doc_row)
            self.db.commit()
            self.db.refresh(doc_row)
            doc_id = doc_row.id

        embeddings = self.embeddings.embed_documents(documents)
        for chunk, embedding in zip(documents, embeddings):
            row = DocumentChunk(
                tenant_id=tenant_id,
                doc_id=doc_id,
                source=source,
                chunk=chunk,
                embedding=embedding,
            )
            self.db.add(row)
        self.db.commit()
