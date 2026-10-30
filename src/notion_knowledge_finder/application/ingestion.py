from __future__ import annotations

import re
from typing import Protocol

from notion_knowledge_finder.config import Settings
from notion_knowledge_finder.infrastructure.notion.client import NotionClient, NotionPage


class RebuildableIndex(Protocol):
    def rebuild(self, pages: list[NotionPage]) -> int: ...


def split_text(text: str, size: int = 1200, overlap: int = 180) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = max(text.rfind("\n", start, end), text.rfind("。", start, end))
            if boundary > start + size // 2:
                end = boundary + 1
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def sync_notion(settings: Settings, index: RebuildableIndex) -> tuple[int, int]:
    pages = list(NotionClient(settings.notion_api_key).fetch_pages())
    return len(pages), index.rebuild(pages)
