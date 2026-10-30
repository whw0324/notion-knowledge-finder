# Notion AI Knowledge Assistant

[English](README.md) | [繁體中文](README.zh.md)

A working full-stack Retrieval-Augmented Generation application for company knowledge. It ingests authorized Notion pages, converts the content into a searchable vector index, and generates source-cited answers through semantic retrieval and a large language model.

> **Project status:** Full-stack MVP completed · Actively improving

![Notion AI Knowledge Assistant chat interface](docs/assets/knowledge-assistant-chat.jpg)

## Highlights

- Built an end-to-end **Notion → Chunking → Embedding → Chroma → LLM** RAG pipeline.
- Developed a **React + TypeScript** interface for chat, indexed documents, sync jobs, and runtime settings.
- Exposed versioned **FastAPI REST APIs** with a layered Controller, Service, Infrastructure, and RAG architecture.
- Used **LangGraph** to orchestrate retrieval, evidence evaluation, and answer/no-answer routing to reduce unsupported responses.
- Persisted conversations, messages, citations, document states, and sync jobs with **SQLAlchemy and Alembic**.
- Supported zero-configuration **SQLite** development and optional **PostgreSQL** deployment, while keeping vector search in Chroma.
- Added **LangChain provider adapters** for configurable Gemini/OpenAI chat and embedding models.
- Returned Notion links, excerpts, and relevance scores so users can verify the evidence behind each answer.

## Problem

Company knowledge is often distributed across hundreds of Notion pages. Employees may know that information exists without remembering the exact title or location, while keyword search performs poorly when a question and a document use different wording.

This application maps questions and document chunks into the same semantic vector space. Chroma retrieves the most relevant content, and LangGraph checks the retrieval score before allowing the language model to answer. When the evidence is insufficient, the workflow explicitly refuses to invent an answer.

## Architecture

```mermaid
flowchart LR
    U[React + TypeScript] -->|REST API| A[FastAPI]
    A --> S[Application Services]
    S --> D[(SQLite / PostgreSQL)]
    S --> G[LangGraph RAG Workflow]

    N[Notion API] --> P[Block / Table Parser]
    P --> C[Text Chunking]
    C --> E[Gemini / OpenAI Embedding]
    E --> V[(Chroma Vector DB)]

    G --> Q[Query Embedding]
    Q --> V
    V -->|Top-K Chunks| G
    G --> L[Gemini / OpenAI Chat]
    L -->|Answer + Citations| A
```

### Ingestion pipeline

```text
Notion API
→ Parse pages, nested blocks, and tables
→ Normalize and split text into chunks
→ Generate embeddings
→ Store vectors, source text, and metadata in Chroma
→ Store document and sync state in the relational database
```

### Question-answering pipeline

```text
User question
→ Query embedding
→ Chroma cosine-similarity search
→ LangGraph relevance threshold
→ Insufficient evidence: refuse to answer
→ Sufficient evidence: send Top-K chunks to the chat model
→ Return answer, Notion sources, and relevance scores
```

## Technology Stack

| Layer | Technologies | Responsibility |
| --- | --- | --- |
| Frontend | React 19, TypeScript, Vite | Chat, documents, sync, and settings UI |
| Client state | TanStack Query, React Router | Server-state caching, mutations, and routing |
| Backend | Python, FastAPI, Pydantic | REST APIs, DTO validation, and dependencies |
| AI orchestration | LangGraph, LangChain | RAG control flow and provider abstraction |
| LLM / Embedding | Gemini or OpenAI | Answer generation and semantic vectors |
| Vector database | Chroma | Chunks, metadata, embeddings, and similarity search |
| Application database | SQLite or PostgreSQL | Conversations, messages, documents, citations, and jobs |
| Persistence | SQLAlchemy, Alembic | ORM and database migrations |
| Integration | Notion API, HTTPX | Authorized page and block ingestion |
| Quality | Pytest, Ruff, TypeScript compiler | Unit tests, linting, and type checking |

## Features

### Knowledge chat

- Create and persist multiple conversations
- Retain user and assistant message history
- Indicate whether an answer has sufficient supporting evidence
- Display Notion sources, excerpts, and relevance scores

### Notion synchronization

- Read only pages explicitly shared with the Notion integration
- Parse paragraphs, headings, nested blocks, and table rows
- Track sync jobs through `pending → running → completed / failed`
- Record page count, chunk count, and provider errors

### Document visibility

- List indexed Notion pages
- Show each page's chunk count and last-edited timestamp
- Open the original Notion source directly

### Model and storage configuration

- Configure chat and embedding providers independently as Gemini or OpenAI
- Run locally with embedded Chroma and SQLite without separate services
- Switch the application database to PostgreSQL through Docker Compose

## REST API

```text
GET    /api/v1/health
GET    /api/v1/conversations
POST   /api/v1/conversations
GET    /api/v1/conversations/{id}
DELETE /api/v1/conversations/{id}
POST   /api/v1/conversations/{id}/messages
GET    /api/v1/documents
GET    /api/v1/sync-jobs
POST   /api/v1/sync-jobs
GET    /api/v1/sync-jobs/{id}
```

FastAPI Swagger UI: <http://localhost:8000/docs>

## Quick Start

### 1. Requirements

- Python 3.11+
- Node.js 20+
- A Gemini or OpenAI API key
- A read-only Notion Developer Connection API token

### 2. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env

cd frontend
npm install
cd ..
```

If `.env` already exists, do not copy the example again because it would overwrite local credentials.

### 3. Configure `.env`

```env
CHAT_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
GOOGLE_API_KEY=your_Gemini_API_key
NOTION_API_KEY=your_Notion_API_token

DATABASE_URL=sqlite:///./.data/app.db
CORS_ORIGINS=http://localhost:5173
GEMINI_CHAT_MODEL=gemini-flash-latest
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001
CHROMA_PATH=.data/chroma
MIN_RELEVANCE_SCORE=0.32
```

Keep secrets only in the local `.env`. Never commit `.env`, API keys, or `.data/`.

### 4. Start the backend

```bash
source .venv/bin/activate
python -m uvicorn notion_knowledge_finder.main:app --reload
```

Backend: <http://localhost:8000>

### 5. Start the frontend

```bash
cd frontend
npm run dev
```

Frontend: <http://localhost:5173>

Open **Notion Sync** to create the first index, then use **Knowledge Chat** to ask questions.

## Optional PostgreSQL Setup

SQLite is the default and requires no separate service. To use PostgreSQL:

```bash
docker compose up -d postgres
```

Update `.env`:

```env
DATABASE_URL=postgresql+psycopg://notion:notion@localhost:5432/notion_finder
```

Run the migration:

```bash
source .venv/bin/activate
alembic upgrade head
```

## Project Structure

```text
frontend/
├── src/api/                        REST client
├── src/components/                 Application shell
├── src/pages/                      Chat / Documents / Sync / Settings
└── src/styles/                     Responsive UI

src/notion_knowledge_finder/
├── api/
│   ├── routes/                     FastAPI controllers
│   └── schemas/                    Request / response DTOs
├── application/
│   ├── chat_service.py             Conversation + RAG use case
│   ├── ingestion.py                Chunking and ingestion
│   └── sync_service.py             Sync jobs and document state
├── infrastructure/
│   ├── ai/                         LangChain provider adapters
│   ├── database/                   SQLAlchemy models and connection
│   ├── notion/                     Notion API client
│   └── vector/                     Chroma knowledge index
├── rag/graph.py                    LangGraph workflow
├── config.py                       Environment configuration
└── main.py                         FastAPI entry point

migrations/                         Alembic migrations
tests/                              Unit tests
docker-compose.yml                  Optional PostgreSQL service
```

## Verification

```bash
source .venv/bin/activate
python -m pytest -q
ruff check src tests migrations

cd frontend
npm run build
```

Current verification results:

- Python unit tests: **9 passed**
- Ruff lint: **passed**
- TypeScript type check: **passed**
- Vite production build: **passed**

## Current Scope and Roadmap

The current release is a complete single-user, single-Notion-workspace MVP. Conversation history is persisted, but earlier messages are not yet used for query rewriting, so the project does not claim full conversational memory.

Planned extensions:

- Notion OAuth and multiple workspaces
- Authentication, tenant isolation, and document-level ACLs
- Incremental sync, deletion detection, and Notion 429 retry handling
- Durable Redis/Celery-style background jobs
- Streaming responses
- Hybrid search, reranking, and a RAG evaluation dataset

## Security Notes

- The Notion integration can read only pages explicitly shared with it.
- `.env`, Chroma data, and the SQLite database are ignored by Git.
- Prompt instructions are not an authorization mechanism; a multi-user release must enforce ACL filters before retrieval.
