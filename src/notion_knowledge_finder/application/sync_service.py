from __future__ import annotations

from hashlib import sha256

from sqlalchemy import select

from notion_knowledge_finder.application.ingestion import split_text
from notion_knowledge_finder.config import Settings
from notion_knowledge_finder.infrastructure.database.connection import Database
from notion_knowledge_finder.infrastructure.database.models import Document, SyncJob, utc_now
from notion_knowledge_finder.infrastructure.notion.client import NotionClient, NotionPage
from notion_knowledge_finder.infrastructure.vector.chroma_index import KnowledgeIndex


def _save_documents(database: Database, pages: list[NotionPage]) -> None:
    page_ids = {page.page_id for page in pages}
    with database.session() as session:
        existing = {
            document.notion_page_id: document for document in session.scalars(select(Document))
        }
        for page in pages:
            content_hash = sha256(page.text.encode("utf-8")).hexdigest()
            document = existing.get(page.page_id)
            if document is None:
                document = Document(notion_page_id=page.page_id, content_hash=content_hash)
                session.add(document)
            document.title = page.title
            document.url = page.url
            document.last_edited_time = page.last_edited_time
            document.content_hash = content_hash
            document.chunk_count = len(split_text(page.text))
            document.sync_status = "indexed"
            document.updated_at = utc_now()

        for notion_page_id, document in existing.items():
            if notion_page_id not in page_ids:
                document.sync_status = "removed"
                document.chunk_count = 0
                document.updated_at = utc_now()
        session.commit()


def run_sync_job(
    job_id: str,
    database: Database,
    settings: Settings,
    index: KnowledgeIndex,
) -> None:
    with database.session() as session:
        job = session.get(SyncJob, job_id)
        if job is None:
            return
        job.status = "running"
        job.started_at = utc_now()
        session.commit()

    try:
        pages = list(NotionClient(settings.notion_api_key).fetch_pages())
        chunks = index.rebuild(pages)
        _save_documents(database, pages)
        with database.session() as session:
            job = session.get(SyncJob, job_id)
            if job is not None:
                job.status = "completed"
                job.pages_processed = len(pages)
                job.chunks_created = chunks
                job.finished_at = utc_now()
                session.commit()
    except Exception as exc:  # noqa: BLE001 - background jobs must persist provider failures
        with database.session() as session:
            job = session.get(SyncJob, job_id)
            if job is not None:
                job.status = "failed"
                job.error_message = str(exc)
                job.finished_at = utc_now()
                session.commit()
