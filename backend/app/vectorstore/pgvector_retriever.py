import os
from dotenv import load_dotenv
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_postgres import PGVector

from app.config.settings import GCP_PROJECT_ID, PGVECTOR_CONNECTION_STRING
from app.vectorstore.base_vector_retriever import BaseVectorRetriever


class PGVectorRetriever(BaseVectorRetriever):
    def _initialize(self):
        self._gcp_project = GCP_PROJECT_ID
        self._connection_string = PGVECTOR_CONNECTION_STRING
        self._embedding_model = "text-embedding-004"

        if not all([self._gcp_project, self._connection_string]):
            raise ValueError(
                "Please set GCP_PROJECT_ID and PGVECTOR_CONNECTION_STRING."
            )

        embeddings = VertexAIEmbeddings(
            model_name=self._embedding_model, project=self._gcp_project
        )

        self._vector_store = PGVector(
            embeddings=embeddings,
            collection_name=self.collection_name,
            connection=self._connection_string,
        )

        self.retriever = self._vector_store.as_retriever(
            search_type=self.search_type, search_kwargs={"k": self.k}
        )
