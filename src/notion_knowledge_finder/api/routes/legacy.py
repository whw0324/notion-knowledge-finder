from fastapi import APIRouter, HTTPException

from notion_knowledge_finder.api.dependencies import get_index
from notion_knowledge_finder.application.ingestion import sync_notion
from notion_knowledge_finder.config import get_settings
from notion_knowledge_finder.models import AskRequest, AskResponse, Source, SyncResponse
from notion_knowledge_finder.rag.graph import build_graph

router = APIRouter(tags=["legacy"])


@router.post("/sync", response_model=SyncResponse, deprecated=True)
def sync_legacy():
    try:
        pages, chunks = sync_notion(get_settings(), get_index())
        return SyncResponse(pages=pages, chunks=chunks)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/ask", response_model=AskResponse, deprecated=True)
def ask_legacy(request: AskRequest):
    try:
        result = build_graph(get_settings(), get_index()).invoke({"question": request.question})
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
