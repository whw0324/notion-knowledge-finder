# Notion AI Knowledge Assistant

[English](README.md) | [繁體中文](README.zh.md)

一個可執行的全端 RAG（Retrieval-Augmented Generation）企業知識助理。系統會擷取已授權的 Notion 頁面，將內容轉換為向量索引，並透過語意檢索與大型語言模型產生附帶來源引用的回答。

> **Project status:** Full-stack MVP completed · 持續改進中

![Notion AI Knowledge Assistant 聊天介面](docs/assets/knowledge-assistant-chat.jpg)

## 專案亮點

- 建立完整的 **Notion → Chunking → Embedding → Chroma → LLM** RAG 資料流程。
- 使用 **React + TypeScript** 開發聊天、文件清單、同步任務與系統設定介面。
- 使用 **FastAPI** 提供版本化 REST API，並以分層架構分離 Controller、Service、Infrastructure 與 RAG Workflow。
- 使用 **LangGraph** 編排「檢索 → 證據判斷 → 回答／拒答」流程，降低缺乏來源時的模型幻覺。
- 使用 **SQLAlchemy + Alembic** 儲存對話、訊息、引用來源、文件狀態與同步任務。
- 支援 **SQLite** 零設定開發與 **PostgreSQL** 部署選項；Chroma 專門負責向量資料與相似度搜尋。
- 透過 **LangChain Provider Adapter** 切換 Gemini／OpenAI Chat 與 Embedding 模型。
- 提供 Notion 來源連結、文字摘錄與相關度分數，讓使用者可以驗證回答依據。

## 解決的問題

公司文件可能散落在大量 Notion 頁面中。使用者知道資料存在，卻不確定文件名稱或位置。傳統關鍵字搜尋也難以處理「意思相近、用詞不同」的問題。

本專案使用 Embedding 將問題與文件片段映射至同一個語意向量空間，再從 Chroma 找出最相關的內容。LangGraph 會檢查檢索分數：證據充足時才將來源交給模型回答；證據不足時則明確拒答。

## 系統架構

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

### RAG 同步流程

```text
Notion API
→ 讀取頁面、巢狀 Blocks 與表格
→ 清理並切分文字（Chunking）
→ 產生 Embedding
→ 將向量、原文與 Metadata 儲存至 Chroma
→ 將文件與同步狀態儲存至關聯式資料庫
```

### RAG 問答流程

```text
使用者問題
→ Query Embedding
→ Chroma Cosine Similarity Search
→ LangGraph 檢查相關度門檻
→ 證據不足：拒絕回答
→ 證據充足：將 Top-K Chunks 交給 Chat Model
→ 回傳回答、Notion 來源與相關度分數
```

## 技術棧

| Layer | Technologies | Responsibility |
| --- | --- | --- |
| Frontend | React 19, TypeScript, Vite | 對話、文件、同步與設定介面 |
| Client state | TanStack Query, React Router | Server-state cache、Mutation、路由 |
| Backend | Python, FastAPI, Pydantic | REST API、DTO 驗證與依賴管理 |
| AI orchestration | LangGraph, LangChain | RAG 流程與模型介面標準化 |
| LLM / Embedding | Gemini or OpenAI | 回答生成與語意向量 |
| Vector database | Chroma | Chunk、Metadata、Embedding 與向量搜尋 |
| Application database | SQLite or PostgreSQL | 對話、訊息、文件、引用與同步任務 |
| Persistence | SQLAlchemy, Alembic | ORM 與資料庫 Migration |
| Integration | Notion API, HTTPX | 授權頁面與 Block 擷取 |
| Quality | Pytest, Ruff, TypeScript compiler | 單元測試、Lint 與型別檢查 |

## 主要功能

### 知識問答

- 建立並保存多個對話
- 顯示使用者與 AI 訊息歷史
- 顯示回答是否有足夠來源支持
- 顯示 Notion 來源、摘錄與相關度

### Notion 同步

- 只讀取明確授權給 Notion Integration 的頁面
- 支援一般文字、標題、巢狀 Blocks 與表格列
- 建立可查詢的同步任務狀態：`pending → running → completed / failed`
- 記錄頁面數量、Chunk 數量與錯誤訊息

### 文件管理

- 查看已索引的 Notion 頁面
- 查看每個頁面的 Chunk 數量與最後更新時間
- 直接開啟原始 Notion 來源

### 模型與儲存

- Chat Model 與 Embedding Model 可分別選擇 Gemini 或 OpenAI
- 預設使用本機 Chroma 與 SQLite，無需額外資料庫服務
- 可透過 Docker Compose 切換至 PostgreSQL

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

FastAPI Swagger UI：<http://localhost:8000/docs>

## 快速啟動

### 1. 環境需求

- Python 3.11+
- Node.js 20+
- Gemini API Key 或 OpenAI API Key
- 具備唯讀權限的 Notion Developer Connection API Token

### 2. 安裝

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env

cd frontend
npm install
cd ..
```

如果 `.env` 已存在，請勿再次複製，以免覆寫本機密鑰。

### 3. 設定 `.env`

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

密鑰只能保存在本機 `.env`。請勿將 `.env`、API Key 或 `.data/` 提交至 Git。

### 4. 啟動後端

```bash
source .venv/bin/activate
python -m uvicorn notion_knowledge_finder.main:app --reload
```

後端：<http://localhost:8000>

### 5. 啟動前端

```bash
cd frontend
npm run dev
```

前端：<http://localhost:5173>

進入 **Notion Sync** 建立第一次索引，完成後即可在 **Knowledge Chat** 中提問。

## PostgreSQL（選用）

預設 SQLite 不需要額外服務。若要使用 PostgreSQL：

```bash
docker compose up -d postgres
```

將 `.env` 改為：

```env
DATABASE_URL=postgresql+psycopg://notion:notion@localhost:5432/notion_finder
```

執行 Migration：

```bash
source .venv/bin/activate
alembic upgrade head
```

## 專案結構

```text
frontend/
├── src/api/                        REST client
├── src/components/                 Application shell
├── src/pages/                      Chat / Documents / Sync / Settings
└── src/styles/                     Responsive UI

src/notion_knowledge_finder/
├── api/
│   ├── routes/                     FastAPI Controllers
│   └── schemas/                    Request / Response DTOs
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

## 驗證

```bash
source .venv/bin/activate
python -m pytest -q
ruff check src tests migrations

cd frontend
npm run build
```

目前驗證結果：

- Python unit tests：**9 passed**
- Ruff lint：**passed**
- TypeScript type check：**passed**
- Vite production build：**passed**

## 目前範圍與後續規劃

目前版本是單一使用者、單一 Notion Workspace 的完整 MVP。現階段對話會被持久化，但 RAG 尚未將先前訊息加入 Query Rewrite，因此不宣稱具備完整的上下文記憶。

後續可擴充：

- Notion OAuth 與多 Workspace
- 使用者登入、Tenant 隔離與文件級 ACL
- 增量同步、刪除偵測與 Notion 429 自動重試
- Redis／Celery 等持久化工作佇列
- Streaming response
- Hybrid Search、Reranker 與 RAG 評估資料集

## 安全性說明

- Notion Integration 只讀取明確分享給它的頁面。
- `.env`、Chroma 資料與 SQLite 資料庫均被 Git 忽略。
- Prompt 限制不是授權機制；正式多使用者版本仍需在檢索前實作 ACL Filter。
