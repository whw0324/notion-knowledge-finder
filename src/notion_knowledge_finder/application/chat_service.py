from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from notion_knowledge_finder.infrastructure.database.models import (
    Conversation,
    Message,
    MessageSource,
    utc_now,
)


class ConversationNotFoundError(LookupError):
    pass


class ChatService:
    def __init__(self, session: Session, graph: Any) -> None:
        self.session = session
        self.graph = graph

    def list_conversations(self) -> list[Conversation]:
        statement = select(Conversation).order_by(Conversation.updated_at.desc())
        return list(self.session.scalars(statement))

    def create_conversation(self, title: str | None = None) -> Conversation:
        conversation = Conversation(title=(title or "New conversation").strip()[:200])
        self.session.add(conversation)
        self.session.commit()
        return conversation

    def get_conversation(self, conversation_id: str) -> Conversation:
        statement = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages).selectinload(Message.sources))
        )
        conversation = self.session.scalar(statement)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation

    def delete_conversation(self, conversation_id: str) -> None:
        conversation = self.session.get(Conversation, conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        self.session.delete(conversation)
        self.session.commit()

    def ask(self, conversation_id: str, content: str) -> Message:
        conversation = self.session.get(Conversation, conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        user_message = Message(conversation_id=conversation.id, role="user", content=content)
        self.session.add(user_message)
        if conversation.title == "New conversation":
            conversation.title = content.strip().replace("\n", " ")[:60]
        conversation.updated_at = utc_now()
        self.session.flush()

        result = self.graph.invoke({"question": content})
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
            grounded=result.get("grounded", False),
        )
        self.session.add(assistant_message)
        self.session.flush()

        for position, hit in enumerate(result.get("hits", []), 1):
            metadata = hit.get("metadata", {})
            assistant_message.sources.append(
                MessageSource(
                    notion_page_id=str(metadata.get("page_id", "")),
                    title=str(metadata.get("title", "Untitled")),
                    url=str(metadata.get("url", "")),
                    excerpt=str(hit.get("text", ""))[:500],
                    score=hit.get("score"),
                    position=position,
                )
            )

        conversation.updated_at = utc_now()
        self.session.commit()
        self.session.refresh(assistant_message)
        return assistant_message
