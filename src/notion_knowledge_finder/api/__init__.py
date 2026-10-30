"""HTTP delivery layer.

``app`` is resolved lazily so the original ``notion_knowledge_finder.api:app``
uvicorn command keeps working without creating an import cycle.
"""


def __getattr__(name: str):
    if name == "app":
        from notion_knowledge_finder.main import app

        return app
    raise AttributeError(name)
