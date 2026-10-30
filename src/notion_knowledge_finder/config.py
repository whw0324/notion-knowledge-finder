from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Notion Knowledge Finder"
    database_url: str = "sqlite:///./.data/app.db"
    cors_origins: str = "http://localhost:5173"
    chat_provider: Literal["openai", "gemini"] = "openai"
    embedding_provider: Literal["openai", "gemini"] = "openai"
    openai_api_key: str = ""
    google_api_key: str = ""
    notion_api_key: str = ""
    openai_chat_model: str = "gpt-5-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    gemini_chat_model: str = "gemini-flash-latest"
    gemini_embedding_model: str = "models/gemini-embedding-001"
    chroma_path: str = ".data/chroma"
    min_relevance_score: float = 0.32

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
