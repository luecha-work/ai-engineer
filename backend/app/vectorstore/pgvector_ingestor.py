from typing import List
from sqlalchemy.orm import Session

from app.vectorstore.base_ingestor import BaseKnowledgeIngestor
from app.models import Document, DocumentChunk
from app.utils.ollama_client import embed_text
from app.utils.text_splitter import split_text


class PGVectorIngestor(BaseKnowledgeIngestor):
    def __init__(self, db: Session):
        self.db = db

    def load_documents(self, file_path: str) -> List[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            return [f.read()]

    def split_documents(self, documents: List[str]) -> List[str]:
        chunks: List[str] = []
        for doc in documents:
            chunks.extend(split_text(doc))
        return chunks

    def embed_and_store(self, documents: List[str], tenant_id: str, source: str, doc_id: int | None = None):
        if doc_id is None:
            doc_row = Document(tenant_id=tenant_id, source=source, content="\\n".join(documents))
            self.db.add(doc_row)
            self.db.commit()
            self.db.refresh(doc_row)
            doc_id = doc_row.id

        for chunk in documents:
            row = DocumentChunk(
                tenant_id=tenant_id,
                doc_id=doc_id,
                source=source,
                chunk=chunk,
                embedding=embed_text(chunk),
            )
            self.db.add(row)
        self.db.commit()

# if __name__ == "__main__":
#     print("🚀 Starting Process: Ingest Knowledge Base to PGVector")

#     docs_path = "/Users/tiscomacnb2479/Documents/Athena (DEV) armor"
#     pdf_list = find_knowledge_base(docs_path)

#     if not pdf_list:
#         print("No PDF files found.")
#     else:
#         print(f"\n🗂 Total PDF files found: {len(pdf_list)}")
#         ingestor = PGVectorIngestor()

#         for item in pdf_list:
#             print(f"\n📥 Folder: {item['subfolder_name']}")
#             ingestor.ingest(
#                 file_path=item['pdf_path'],
#                 collection_name=item['subfolder_name']
#             )

#     print("\n✅ Done ingesting all documents into PGVector.")
