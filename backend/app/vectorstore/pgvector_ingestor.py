import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_postgres import PGVector

from app.config.settings import GCP_PROJECT_ID, PGVECTOR_CONNECTION_STRING

from app.vectorstore.base_ingestor import BaseKnowledgeIngestor
from app.utils.find_knowledge_base_path import find_knowledge_base


class PGVectorIngestor(BaseKnowledgeIngestor):
    def __init__(self):
        self._gcp_project = GCP_PROJECT_ID
        self._connection_string = PGVECTOR_CONNECTION_STRING
        self._embedding_model = "text-embedding-004"
        
        if not self._gcp_project or not self._connection_string:
            raise ValueError(
                "GCP_PROJECT_ID and PGVECTOR_CONNECTION_STRING must be set in .env"
            )

        self.embeddings = VertexAIEmbeddings(
            model_name=self._embedding_model, project=self._gcp_project
        )

    def load_documents(self, file_path: str):
        loader = PyMuPDFLoader(file_path)
        return loader.load()

    def split_documents(self, documents):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return splitter.split_documents(documents)

    def embed_and_store(self, documents, collection_name: str):
        PGVector.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=collection_name,
            connection=self._connection_string,
            pre_delete_collection=False,
        )

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