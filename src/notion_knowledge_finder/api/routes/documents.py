from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from notion_knowledge_finder.api.dependencies import get_db_session
from notion_knowledge_finder.api.schemas.models import DocumentResponse
from notion_knowledge_finder.infrastructure.database.models import Document

router = APIRouter(prefix="/documents", tags=["documents"])
SessionDependency = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=list[DocumentResponse])
def list_documents(session: SessionDependency):
    statement = select(Document).order_by(Document.updated_at.desc())
    return list(session.scalars(statement))
