from typing import Annotated

from fastapi import APIRouter, Depends

from notion_knowledge_finder.api.dependencies import settings_dependency
from notion_knowledge_finder.config import Settings

router = APIRouter(tags=["system"])
SettingsDependency = Annotated[Settings, Depends(settings_dependency)]


@router.get("/health")
def health(settings: SettingsDependency) -> dict:
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
