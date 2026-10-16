from langchain_core.messages import AIMessage

from notion_knowledge_finder.workflow import response_text


def test_response_text_hides_gemini_metadata():
    message = AIMessage(
        content=[
            {
                "type": "text",
                "text": "这是最终答案。",
                "extras": {"signature": "internal-signature"},
            }
        ]
    )

    assert response_text(message) == "这是最终答案。"
