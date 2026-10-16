from notion_knowledge_finder.ingestion import split_text


def test_split_empty():
    assert split_text("  \n") == []


def test_split_keeps_content_with_bounded_chunks():
    text = "第一段。" * 400
    chunks = split_text(text, size=100, overlap=20)
    assert len(chunks) > 1
    assert all(chunks)
    assert all(len(chunk) <= 101 for chunk in chunks)
