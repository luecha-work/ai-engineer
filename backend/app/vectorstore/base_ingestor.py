from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document

class BaseKnowledgeIngestor(ABC):

    @abstractmethod
    def load_documents(self, file_path: str) -> List[Document]:
        """Load documents from a file path"""
        pass

    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        pass

    @abstractmethod
    def embed_and_store(self, documents: List[Document], collection_name: str):
        """Embed and store documents in vector store"""
        pass
    
    

    def ingest(self, file_path: str, collection_name: str):
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
            self.embed_and_store(chunks, collection_name)
            print("✅ Successfully stored in vector store!")
        except Exception as e:
            print(f"Error storing data: {e}")
