from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str
    url: str
    excerpt: str
    score: float | None = None


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


class AskResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
    grounded: bool


class SyncResponse(BaseModel):
    pages: int
    chunks: int
