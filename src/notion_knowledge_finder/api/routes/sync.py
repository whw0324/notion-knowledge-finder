from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from notion_knowledge_finder.api.dependencies import (
    get_database,
    get_db_session,
    get_index,
    settings_dependency,
)
from notion_knowledge_finder.api.schemas.models import SyncJobResponse
from notion_knowledge_finder.application.sync_service import run_sync_job
from notion_knowledge_finder.config import Settings
from notion_knowledge_finder.infrastructure.database.models import SyncJob

router = APIRouter(prefix="/sync-jobs", tags=["notion-sync"])
SessionDependency = Annotated[Session, Depends(get_db_session)]
SettingsDependency = Annotated[Settings, Depends(settings_dependency)]


@router.get("", response_model=list[SyncJobResponse])
def list_sync_jobs(session: SessionDependency):
    statement = select(SyncJob).order_by(SyncJob.created_at.desc()).limit(30)
    return list(session.scalars(statement))


@router.post("", response_model=SyncJobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_sync_job(
    background_tasks: BackgroundTasks,
    session: SessionDependency,
    settings: SettingsDependency,
):
    job = SyncJob()
    session.add(job)
    session.commit()
    session.refresh(job)
    background_tasks.add_task(
        run_sync_job,
        job.id,
        get_database(),
        settings,
        get_index(),
    )
    return job


@router.get("/{job_id}", response_model=SyncJobResponse)
def get_sync_job(job_id: str, session: SessionDependency):
    job = session.get(SyncJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Sync job not found")
    return job
