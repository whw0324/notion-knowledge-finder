from functools import lru_cache

from fastapi import FastAPI, HTTPException

from notion_knowledge_finder.config import Settings, get_settings
from notion_knowledge_finder.ingestion import sync_notion
from notion_knowledge_finder.models import AskRequest, AskResponse, Source, SyncResponse
from notion_knowledge_finder.retrieval import KnowledgeIndex
from notion_knowledge_finder.workflow import build_graph

app = FastAPI(title="Notion Knowledge Finder", version="0.1.0")


@lru_cache
def get_index() -> KnowledgeIndex:
    return KnowledgeIndex(get_settings())


@lru_cache
def get_graph():
    return build_graph(get_settings(), get_index())


def get_services() -> tuple[Settings, KnowledgeIndex]:
    return get_settings(), get_index()


@app.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "chat_provider": settings.chat_provider,
        "embedding_provider": settings.embedding_provider,
        "chat_model": (
            settings.gemini_chat_model
            if settings.chat_provider == "gemini"
            else settings.openai_chat_model
        ),
        "embedding_model": (
            settings.gemini_embedding_model
            if settings.embedding_provider == "gemini"
            else settings.openai_embedding_model
        ),
    }


@app.post("/sync", response_model=SyncResponse)
def sync():
    try:
        settings, index = get_services()
        pages, chunks = sync_notion(settings, index)
        return SyncResponse(pages=pages, chunks=chunks)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        result = get_graph().invoke({"question": request.question})
        sources = [
            Source(
                title=hit["metadata"]["title"],
                url=hit["metadata"]["url"],
                excerpt=hit["text"][:280],
                score=hit["score"],
            )
            for hit in result.get("hits", [])
        ]
        return AskResponse(answer=result["answer"], sources=sources, grounded=result["grounded"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
