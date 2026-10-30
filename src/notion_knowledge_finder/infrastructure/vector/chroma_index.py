from __future__ import annotations

from dataclasses import asdict

import chromadb

from notion_knowledge_finder.application.ingestion import split_text
from notion_knowledge_finder.config import Settings
from notion_knowledge_finder.infrastructure.ai.providers import build_embeddings
from notion_knowledge_finder.infrastructure.notion.client import NotionPage


class KnowledgeIndex:
    def __init__(self, settings: Settings) -> None:
        client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = client.get_or_create_collection(
            "notion_pages", metadata={"hnsw:space": "cosine"}
        )
        self.embeddings = build_embeddings(settings)

    def rebuild(self, pages: list[NotionPage]) -> int:
        ids, docs, metadata = [], [], []
        for page in pages:
            for number, chunk in enumerate(split_text(page.text)):
                ids.append(f"{page.page_id}:{number}")
                docs.append(chunk)
                item = asdict(page)
                item.pop("text")
                item["chunk"] = number
                metadata.append(item)
        current = self.collection.get(include=[]).get("ids", [])
        if current:
            self.collection.delete(ids=current)
        if docs:
            self.collection.add(
                ids=ids,
                documents=docs,
                metadatas=metadata,
                embeddings=self.embeddings.embed_documents(docs),
            )
        return len(docs)

    def search(self, query: str, limit: int = 6) -> list[dict]:
        if self.collection.count() == 0:
            return []
        result = self.collection.query(
            query_embeddings=[self.embeddings.embed_query(query)],
            n_results=min(limit, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        return [
            {"text": doc, "metadata": meta, "score": round(1 - distance, 4)}
            for doc, meta, distance in zip(
                result["documents"][0], result["metadatas"][0], result["distances"][0]
            )
        ]
