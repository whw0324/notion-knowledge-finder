from notion_knowledge_finder.config import get_settings
from notion_knowledge_finder.ingestion import sync_notion
from notion_knowledge_finder.retrieval import KnowledgeIndex


def main() -> None:
    settings = get_settings()
    pages, chunks = sync_notion(settings, KnowledgeIndex(settings))
    print(f"Synced {pages} pages and {chunks} chunks")


if __name__ == "__main__":
    main()
