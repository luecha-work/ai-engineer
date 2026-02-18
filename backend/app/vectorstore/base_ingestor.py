from abc import ABC, abstractmethod
from typing import List


class BaseKnowledgeIngestor(ABC):
    @abstractmethod
    def load_documents(self, file_path: str) -> List[str]:
        """Load raw documents from a file path."""

    @abstractmethod
    def split_documents(self, documents: List[str]) -> List[str]:
        """Split documents into smaller chunks."""

    @abstractmethod
    def embed_and_store(self, documents: List[str], tenant_id: str, source: str, doc_id: int | None = None):
        """Embed and store documents in vector store."""

    def ingest(self, file_path: str, tenant_id: str, source: str, doc_id: int | None = None):
        print(f"Reading file from: {file_path}")
        try:
            documents = self.load_documents(file_path)
            if not documents:
                print("No content found in the file.")
                return
        except Exception as e:
            print(f"Error loading file: {e}")
            return

        chunks = self.split_documents(documents)
        print(f"Document is now split into {len(chunks)} chunks.")

        try:
            self.embed_and_store(chunks, tenant_id, source, doc_id)
            print("✅ Successfully stored in vector store!")
        except Exception as e:
            print(f"Error storing data: {e}")
