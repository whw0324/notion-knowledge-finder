from __future__ import annotations

from typing import Literal, TypedDict

from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from notion_knowledge_finder.config import Settings
from notion_knowledge_finder.infrastructure.ai.providers import build_chat_model
from notion_knowledge_finder.infrastructure.vector.chroma_index import KnowledgeIndex


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
                "I could not find enough reliable evidence in the synced Notion content. "
                "Try rephrasing the question or confirm that the relevant page is shared "
                "with the Notion integration."
            ),
            "grounded": False,
        }

    def answer(state: RAGState) -> dict:
        context = "\n\n".join(
            f"[Source {i}] Title: {hit['metadata']['title']}\nContent: {hit['text']}"
            for i, hit in enumerate(state["hits"], 1)
        )
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are an internal company knowledge assistant. Answer only from "
                        "the provided sources and do not introduce unsupported facts. Keep "
                        "the answer direct and concise, cite relevant claims with [Source N], "
                        "and clearly identify conflicting or insufficient evidence. Answer in "
                        "the same language as the user's question."
                    )
                ),
                HumanMessage(content=f"Question: {state['question']}\n\n{context}"),
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
