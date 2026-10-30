from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from notion_knowledge_finder.api.dependencies import get_database
from notion_knowledge_finder.api.routes import conversations, documents, health, legacy, sync
from notion_knowledge_finder.config import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_database().create_tables()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(health.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")
app.include_router(legacy.router)
