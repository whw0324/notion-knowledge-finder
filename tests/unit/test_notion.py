from notion_knowledge_finder.notion import NotionClient


def test_block_text_reads_table_cells():
    block = {
        "type": "table_row",
        "table_row": {
            "cells": [
                [{"plain_text": "HashMap"}],
                [{"plain_text": "put()"}, {"plain_text": " / get()"}],
                [{"plain_text": "频率统计"}],
            ]
        },
    }

    assert NotionClient._block_text(block) == "HashMap | put() / get() | 频率统计"


def test_block_text_still_reads_paragraphs():
    block = {
        "type": "paragraph",
        "paragraph": {"rich_text": [{"plain_text": "普通段落"}]},
    }

    assert NotionClient._block_text(block) == "普通段落"
