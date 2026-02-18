from abc import ABC, abstractmethod
from typing import Optional


class BaseVectorRetriever(ABC):
    def __init__(
        self, collection_name: str, k: int = 3, search_type: str = "similarity"
    ):
        self.collection_name = collection_name
        self.k = k
        self.search_type = search_type
        self.retriever = None
        self._vector_store = None
        self._initialize()

    @abstractmethod
    def _initialize(self):
        pass

    def get_context(self, query: str) -> str:
        if not self.retriever:
            raise ValueError("Retriever is not set up. Call setup_vectorstore() first.")

        try:
            docs = self.retriever.invoke(query)
            return "\n\n".join(
                f"[{i+1}] {doc.metadata.get('title', '')}\n{doc.page_content}"
                for i, doc in enumerate(docs)
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve context: {e}")
