from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from notion_knowledge_finder.config import Settings


def build_chat_model(settings: Settings) -> BaseChatModel:
    """Create the configured chat model without leaking provider details elsewhere."""
    if settings.chat_provider == "gemini":
        if not settings.google_api_key:
            raise ValueError("CHAT_PROVIDER=gemini 时必须设置 GOOGLE_API_KEY")

        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_chat_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )

    if not settings.openai_api_key:
        raise ValueError("CHAT_PROVIDER=openai 时必须设置 OPENAI_API_KEY")

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )


def build_embeddings(settings: Settings) -> Embeddings:
    """Create embeddings independently so chat and retrieval providers can differ."""
    if settings.embedding_provider == "gemini":
        if not settings.google_api_key:
            raise ValueError("EMBEDDING_PROVIDER=gemini 时必须设置 GOOGLE_API_KEY")

        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=settings.gemini_embedding_model,
            google_api_key=settings.google_api_key,
        )

    if not settings.openai_api_key:
        raise ValueError("EMBEDDING_PROVIDER=openai 时必须设置 OPENAI_API_KEY")

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )
