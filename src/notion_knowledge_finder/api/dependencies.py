from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy.orm import Session

from notion_knowledge_finder.config import Settings, get_settings
from notion_knowledge_finder.infrastructure.database.connection import Database
from notion_knowledge_finder.infrastructure.vector.chroma_index import KnowledgeIndex
from notion_knowledge_finder.rag.graph import build_graph


@lru_cache
def get_database() -> Database:
    return Database(get_settings().database_url)


@lru_cache
def get_index() -> KnowledgeIndex:
    return KnowledgeIndex(get_settings())


@lru_cache
def get_graph():
    return build_graph(get_settings(), get_index())


def get_db_session() -> Iterator[Session]:
    with get_database().session() as session:
        yield session


def settings_dependency() -> Settings:
    return get_settings()
