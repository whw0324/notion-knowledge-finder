# Notion Knowledge Finder

面向公司内部知识的 RAG 搜索助手：同步有权限访问的 Notion 页面，使用向量检索找出相关段落，再通过 LangGraph 控制“回答 / 拒答”路径。回答附带可点击的 Notion 原文链接。

## 1. 配置 Notion

1. 在 Notion 的 **Settings → Connections / Integrations** 创建 Internal Integration。
2. 将需要搜索的页面或 Teamspace 共享给该 Integration；API 只能读取明确授权的内容。
3. 复制 `.env.example` 为 `.env`，填写 `NOTION_API_KEY`，然后选择 OpenAI 或 Gemini。

### 使用 Gemini（推荐先用这个跑通）

```env
CHAT_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
GOOGLE_API_KEY=替换成新生成的_Key

GEMINI_CHAT_MODEL=gemini-flash-latest
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001
```

API Key 只放在本地 `.env`，不要提交到 Git、写入源代码或粘贴到聊天记录。Key 一旦公开，
应立即在 Google AI Studio 中删除并重新生成。

### 使用 OpenAI

```env
CHAT_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=替换成你的_Key

OPENAI_CHAT_MODEL=gpt-5-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

聊天和 Embedding 可使用不同供应商。例如 Gemini 负责回答、OpenAI 负责向量化：

```env
CHAT_PROVIDER=gemini
EMBEDDING_PROVIDER=openai
GOOGLE_API_KEY=替换成你的_Gemini_Key
OPENAI_API_KEY=替换成你的_OpenAI_Key
```

修改 `EMBEDDING_PROVIDER` 或 Embedding 模型后，必须再次“同步 Notion”，重建 Chroma
中的文档向量。同一个 collection 不能混用不同模型生成的向量。

## 2. 启动

使用 `uv`：

```bash
uv sync --extra dev
uv run uvicorn notion_knowledge_finder.api:app --reload
```

如果尚未安装 `uv`，也可以使用标准 Python：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn notion_knowledge_finder.api:app --reload
```

另开一个终端启动界面：

```bash
uv run streamlit run frontend/streamlit_app.py  # 使用 uv
# 或 streamlit run frontend/streamlit_app.py    # 使用已激活的 venv
```

打开 http://localhost:8501，先点击侧边栏的“同步 Notion”，然后开始提问。

也可以直接调用 API：

```bash
curl -X POST http://localhost:8000/sync
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"报销流程是什么？"}'
```

## 架构

```text
Notion API → 递归读取页面 blocks → 分块 → 可选 Embeddings → Chroma
                                                             ↓
用户问题 → 向量检索 → 相关度门槛 → LangGraph → 可选聊天模型 → 引用式回答 / 明确拒答
```

## 目录结构

```text
frontend/                      Streamlit 前端
scripts/                       独立运维脚本
src/notion_knowledge_finder/   后端 Python 包
├── api.py                     FastAPI 接口与依赖生命周期
├── config.py                  环境配置
├── ingestion.py               文本分块与同步流程
├── models.py                  API 数据模型
├── notion.py                  Notion API 集成
├── providers.py               OpenAI / Gemini 模型工厂
├── retrieval.py               Chroma 检索索引
└── workflow.py                LangGraph RAG 工作流
tests/
├── unit/                      单元测试
└── integration/               集成测试
```

不启动 API 也可以单独同步：

```bash
uv run python scripts/sync_notion.py
```

## 上生产前建议

- 将“全量重建”改为按 `last_edited_time` 增量同步，并用定时任务触发。
- 根据员工身份过滤文档权限；不要让索引扩大用户原有的 Notion 权限。
- 加入搜索反馈、无结果问题统计和离线检索评测集。
- 数据量较大时把 Chroma 换为带备份的 pgvector 或 Qdrant。
