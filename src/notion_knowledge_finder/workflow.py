from __future__ import annotations

from typing import Literal, TypedDict

from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from notion_knowledge_finder.config import Settings
from notion_knowledge_finder.providers import build_chat_model
from notion_knowledge_finder.retrieval import KnowledgeIndex


class RAGState(TypedDict, total=False):
    question: str
    hits: list[dict]
    answer: str
    grounded: bool


def response_text(response) -> str:
    """Return message text without exposing provider-specific metadata."""
    return response.text


def build_graph(settings: Settings, index: KnowledgeIndex):
    llm = build_chat_model(settings)

    def retrieve(state: RAGState) -> dict:
        return {"hits": index.search(state["question"])}

    def route(state: RAGState) -> Literal["answer", "no_answer"]:
        hits = state.get("hits", [])
        if hits and hits[0]["score"] >= settings.min_relevance_score:
            return "answer"
        return "no_answer"

    def no_answer(_: RAGState) -> dict:
        return {
            "answer": (
                "我在当前已同步的 Notion 内容中没有找到足够可靠的答案。"
                "你可以换一种问法，或确认相关页面已共享给 Notion Integration。"
            ),
            "grounded": False,
        }

    def answer(state: RAGState) -> dict:
        context = "\n\n".join(
            f"[来源 {i}] 标题：{hit['metadata']['title']}\n内容：{hit['text']}"
            for i, hit in enumerate(state["hits"], 1)
        )
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "你是公司内部知识检索助手。只能根据给定来源回答；"
                        "不得补充来源中没有的事实。回答要直接、简洁，"
                        "并在相关陈述后标注 [来源 N]。"
                        "如果证据冲突或不足，要明确说明。"
                    )
                ),
                HumanMessage(content=f"问题：{state['question']}\n\n{context}"),
            ]
        )
        return {"answer": response_text(response), "grounded": True}

    builder = StateGraph(RAGState)
    builder.add_node("retrieve", retrieve)
    builder.add_node("answer", answer)
    builder.add_node("no_answer", no_answer)
    builder.add_edge(START, "retrieve")
    builder.add_conditional_edges("retrieve", route)
    builder.add_edge("answer", END)
    builder.add_edge("no_answer", END)
    return builder.compile()
