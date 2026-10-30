from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    url: str
    excerpt: str
    score: float | None = None


class MessageCreate(BaseModel):
    content: str = Field(min_length=2, max_length=4000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    role: str
    content: str
    grounded: bool | None
    created_at: datetime
    sources: list[SourceResponse] = Field(default_factory=list)


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationSummary):
    messages: list[MessageResponse] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    notion_page_id: str
    title: str
    url: str
    last_edited_time: str
    chunk_count: int
    sync_status: str
    updated_at: datetime


class SyncJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    pages_processed: int
    chunks_created: int
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
