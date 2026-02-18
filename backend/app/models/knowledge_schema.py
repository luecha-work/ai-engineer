from pydantic import BaseModel, Field
from typing import List


class TenantCreate(BaseModel):
    id: str = Field(..., description="Tenant identifier")
    name: str


class DocumentIn(BaseModel):
    source: str
    content: str


class IngestRequest(BaseModel):
    tenant_id: str
    documents: List[DocumentIn]


class QueryRequest(BaseModel):
    tenant_id: str
    question: str


class QueryResponse(BaseModel):
    answer: str
    citations: List[str]
    cached: bool
