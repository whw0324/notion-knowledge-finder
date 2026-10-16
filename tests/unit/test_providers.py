import pytest
from pydantic import ValidationError

from notion_knowledge_finder.config import Settings
from notion_knowledge_finder.providers import build_chat_model, build_embeddings


def test_gemini_chat_requires_key():
    settings = Settings(_env_file=None, chat_provider="gemini", google_api_key="")

    with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
        build_chat_model(settings)


def test_gemini_embeddings_require_key():
    settings = Settings(_env_file=None, embedding_provider="gemini", google_api_key="")

    with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
        build_embeddings(settings)


def test_unknown_provider_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, chat_provider="unknown")
