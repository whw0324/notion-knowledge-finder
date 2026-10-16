from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class NotionPage:
    page_id: str
    title: str
    url: str
    last_edited_time: str
    text: str


class NotionClient:
    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("NOTION_API_KEY is missing")
        self.client = httpx.Client(
            base_url="https://api.notion.com/v1",
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2026-03-11",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

    def _pages(self) -> Iterator[dict[str, Any]]:
        cursor = None
        while True:
            payload: dict[str, Any] = {
                "page_size": 100,
                "filter": {"property": "object", "value": "page"},
            }
            if cursor:
                payload["start_cursor"] = cursor
            response = self.client.post("/search", json=payload)
            response.raise_for_status()
            body = response.json()
            yield from body["results"]
            if not body.get("has_more"):
                return
            cursor = body["next_cursor"]

    def _children(self, block_id: str) -> Iterator[dict[str, Any]]:
        cursor = None
        while True:
            params: dict[str, Any] = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            response = self.client.get(f"/blocks/{block_id}/children", params=params)
            response.raise_for_status()
            body = response.json()
            for block in body["results"]:
                yield block
                if block.get("has_children"):
                    yield from self._children(block["id"])
            if not body.get("has_more"):
                return
            cursor = body["next_cursor"]

    @staticmethod
    def _title(page: dict[str, Any]) -> str:
        for prop in page.get("properties", {}).values():
            if prop.get("type") == "title":
                title = "".join(item.get("plain_text", "") for item in prop.get("title", []))
                return title or "Untitled"
        return "Untitled"

    @staticmethod
    def _block_text(block: dict[str, Any]) -> str:
        block_type = block.get("type", "")
        value = block.get(block_type, {})
        if block_type == "table_row" and isinstance(value, dict):
            cells = value.get("cells", [])
            return " | ".join(
                "".join(item.get("plain_text", "") for item in cell) for cell in cells
            )

        rich_text = value.get("rich_text", []) if isinstance(value, dict) else []
        text = "".join(item.get("plain_text", "") for item in rich_text)
        return f"\n{text}\n" if block_type.startswith("heading") else text

    def fetch_pages(self) -> Iterator[NotionPage]:
        for page in self._pages():
            text = "\n".join(
                filter(None, (self._block_text(block) for block in self._children(page["id"])))
            )
            if text.strip():
                yield NotionPage(
                    page_id=page["id"],
                    title=self._title(page),
                    url=page.get("url", ""),
                    last_edited_time=page.get("last_edited_time", ""),
                    text=text,
                )
