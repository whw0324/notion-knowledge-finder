from notion_knowledge_finder.application.chat_service import ChatService
from notion_knowledge_finder.infrastructure.database.connection import Database


class FakeGraph:
    def invoke(self, state):
        assert state["question"] == "What is RAG?"
        return {
            "answer": "Retrieval augmented generation [来源 1]",
            "grounded": True,
            "hits": [
                {
                    "text": "RAG retrieves context before generation.",
                    "metadata": {
                        "page_id": "page-1",
                        "title": "RAG Guide",
                        "url": "https://notion.so/rag",
                    },
                    "score": 0.91,
                }
            ],
        }


def test_conversation_and_answer_are_persisted():
    database = Database("sqlite:///:memory:")
    database.create_tables()

    with database.session() as session:
        service = ChatService(session, FakeGraph())
        conversation = service.create_conversation()
        answer = service.ask(conversation.id, "What is RAG?")

        assert answer.role == "assistant"
        assert answer.grounded is True
        assert answer.sources[0].title == "RAG Guide"

        stored = service.get_conversation(conversation.id)
        assert stored.title == "What is RAG?"
        assert [message.role for message in stored.messages] == ["user", "assistant"]
