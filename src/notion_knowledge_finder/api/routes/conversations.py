from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from notion_knowledge_finder.api.dependencies import get_db_session, get_graph
from notion_knowledge_finder.api.schemas.models import (
    ConversationCreate,
    ConversationDetail,
    ConversationSummary,
    MessageCreate,
    MessageResponse,
)
from notion_knowledge_finder.application.chat_service import (
    ChatService,
    ConversationNotFoundError,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])
SessionDependency = Annotated[Session, Depends(get_db_session)]


def service(session: SessionDependency) -> ChatService:
    return ChatService(session, get_graph())


ChatDependency = Annotated[ChatService, Depends(service)]


@router.get("", response_model=list[ConversationSummary])
def list_conversations(chat: ChatDependency):
    return chat.list_conversations()


@router.post("", response_model=ConversationSummary, status_code=status.HTTP_201_CREATED)
def create_conversation(
    chat: ChatDependency,
    request: ConversationCreate | None = None,
):
    return chat.create_conversation(request.title if request else None)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str, chat: ChatDependency):
    try:
        return chat.get_conversation(conversation_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str, chat: ChatDependency):
    try:
        chat.delete_conversation(conversation_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
def create_message(
    conversation_id: str,
    request: MessageCreate,
    chat: ChatDependency,
):
    try:
        return chat.ask(conversation_id, request.content)
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
