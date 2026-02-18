# Internal Knowledge Assistant (AI Engineer Build Test)

## Overview
This project implements **Option C – Internal Knowledge Assistant**. It provides a minimal backend service that ingests internal documents per tenant, stores them in PostgreSQL, indexes embeddings in **pgvector**, uses Redis for caching, and answers employee questions with citations and a safe refusal when context is missing. The LLM and embedding model are served via **Ollama** in a container.

## Section A — Core AI System Design

### A1. Problem Framing
- **User**: Internal employees (Operations, HR, Marketing, Support) who need quick answers from internal documents.
- **Decision**: Determine accurate answers and locate the source documents to support business actions.
- **Why rules are insufficient**: Document content changes frequently and is unstructured. Rule-based systems struggle with semantic matching, natural language queries, and content summarization across many documents.

### A2. System Architecture
- **API Layer**: FastAPI
- **LLM Usage**: Ollama (`llama3:8b`) for generation
- **Embedding Model**: Ollama (`nomic-embed-text`) for embeddings
- **Prompt Layer**: System + user prompt with refusal behavior
- **PostgreSQL**: System-of-record for tenants, documents, requests, results, audit
- **Vector DB**: pgvector for embeddings + semantic search (PostgreSQL extension)
- **Redis**: Cache responses per tenant + question

**Flow (high-level)**
1. `POST /knowledge/ingest` stores documents in PostgreSQL.
2. Documents are chunked and embedded, then stored in `document_chunks` with pgvector and `tenant_id`.
3. `POST /knowledge/query` retrieves relevant chunks (scoped by tenant), builds a prompt, and returns an answer + citations.
4. Results are stored in PostgreSQL; responses cached in Redis.

### A3. Data Model (Minimal)
- **Tenant**: `id`, `name`
- **Document**: `id`, `tenant_id`, `source`, `content`
- **DocumentChunk**: `id`, `tenant_id`, `doc_id`, `source`, `chunk`, `embedding`
- **AIRequest**: `id`, `tenant_id`, `question`
- **AIResult**: `id`, `request_id`, `tenant_id`, `answer`, `citations`

**Tenant enforcement**: Every table has `tenant_id`. All reads and vector retrieval filter by `tenant_id`.

### A4. Prompt Design (Example)
System prompt:
- "You are an internal knowledge assistant. Use only the provided context. If the answer is not in the context, respond with: I don't have enough context to answer that question based on the available documents. Do not guess."

User prompt:
- "Question: {question}\nContext: {top_chunks}\nAnswer in a concise paragraph."

**Why structured**: Clear refusal behavior reduces hallucinations and makes outputs explainable to business users.

## Section B — Data, RAG & Safety
**B1. RAG Design**
- **Chunking**: Split documents into ~500 character chunks.
- **Embeddings**: `nomic-embed-text` via Ollama.
- **Tenant filtering**: SQL filter on `tenant_id` during vector retrieval.

## Section D — Multi-Tenant & Scale Thinking
**D1. Tenant Isolation Strategy**
- **Prompt isolation**: Only tenant-scoped chunks are included in the prompt.
- **Vector scope**: SQL filter ensures cross-tenant vectors are never retrieved.
- **Database isolation**: All queries include `tenant_id` in WHERE clauses.

## Section E — Execution Reality Check
1. **Ship in 2 weeks**: MVP with ingestion, retrieval, caching, and basic audit logs.
2. **Not build yet**: Fine-tuning, admin UI, advanced analytics.
3. **Risks**: Hallucination risk, tenant leakage, LLM cost control, stale or missing data.

## Assumptions
- Local Ollama is acceptable for demo usage.
- `pgvector` extension is enabled at startup.

## Trade-offs
- Minimal chunking and embedding logic for speed.
- No authentication layer included (out of scope for 90 minutes).

## Improvements With More Time
- Role-based access control
- Better chunking (semantic or token-based)
- Evaluation pipeline and feedback loop

## Runbook
### Prerequisites
- Docker
- Docker Compose

### One-command startup
```bash
docker compose up --build
```

### Pull Ollama models (first run)
```bash
docker exec -it aiengineer-ollama-1 ollama pull nomic-embed-text
docker exec -it aiengineer-ollama-1 ollama pull llama3:8b
```

### Environment variables
See `.env.example` for reference.

### Health checks
```bash
curl http://localhost:8000/health
```

### Swagger UI
```text
http://localhost:8000/docs
```

### Example API calls (end-to-end)
```bash
curl -X POST http://localhost:8000/knowledge/tenants \
  -H "Content-Type: application/json" \
  -d '{"id":"tenant_a","name":"Tenant A"}'

curl -X POST http://localhost:8000/knowledge/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id":"tenant_a",
    "documents":[
      {"source":"handbook.md","content":"Employees must submit PTO requests 2 weeks in advance."},
      {"source":"it-policy.md","content":"All laptops must be encrypted and locked when unattended."}
    ]
  }'

curl -X POST http://localhost:8000/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant_a","question":"How far in advance should PTO be requested?"}'
```

## Repo Structure
- `backend/` FastAPI service
- `src/` placeholder for future shared libs
- `infra/` placeholder for infra scripts
- `docker-compose.yml` local stack
