"""What every research source tool shares: documents in, evidence out (R1 topic 3).

A source tool answers the model with text and carries the documents it fetched as the
``ToolMessage``'s ``artifact`` (``response_format="content_and_artifact"``). ``documents_read``
collects those artifacts from a run's messages: they are the only evidence the claim check
accepts, so a claim can only rest on a document a tool returned, never on text the model wrote.

``available_sources`` says which sources this environment can serve: the web always, academic
search when Exa's key is set, and the documents source when P2's index of this project has been
built. ``research_sources`` adds the documents source for a run whose caller gave it files.
"""

import os
from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AnyMessage, ToolMessage

from agentlab.configs.paths_config import CHROMA_DIR
from agentlab.configs.research_config import (
    EXA_KEY_ENV,
    PROJECT_DOCUMENTS,
    SOURCE_TOOLS,
)
from agentlab.schemas.input.research_input_schema import ResearchOptions, SourceName
from agentlab.schemas.output.research_output_schema import SourceDocument, join_text


def as_artifact(documents: Sequence[SourceDocument]) -> list[dict[str, Any]]:
    """Documents as plain dicts: an artifact is checkpointed with the messages."""
    return [document.model_dump() for document in documents]


def format_documents(documents: Sequence[SourceDocument]) -> str:
    """The text the model reads: each document's reference, title, and text."""
    return "\n\n---\n\n".join(
        "\n".join(filter(None, [document.url, document.title])) + f"\n\n{document.text}"
        for document in documents
    )


def documents_read(messages: Sequence[AnyMessage]) -> dict[str, SourceDocument]:
    """Every document the run's source tools returned, keyed by URL. Failed calls carry none."""
    documents: dict[str, SourceDocument] = {}
    for message in messages:
        if (
            isinstance(message, ToolMessage)
            and message.status != "error"
            and isinstance(message.artifact, list)
        ):
            for item in message.artifact:
                document = SourceDocument.model_validate(item)
                if earlier := documents.get(document.url):
                    document = document.model_copy(
                        update={"text": join_text(earlier.text, document.text)}
                    )
                documents[document.url] = document
    return documents


def available_sources() -> list[SourceName]:
    """The sources this environment can serve, in ``SOURCE_TOOLS`` order."""
    ready: dict[str, bool] = {
        "web": True,
        "academic": bool(os.getenv(EXA_KEY_ENV)),
        "documents": CHROMA_DIR.exists(),
    }
    return [name for name in SOURCE_TOOLS if ready[name]]  # type: ignore[misc]


def research_sources(
    options: ResearchOptions,
) -> tuple[list[SourceName], list[SourceName]]:
    """The sources a research run may use, and the requested ones this environment can't serve.

    ``options.sources`` is what the caller allows: ``None`` means every available source. Files
    in ``options.documents`` make the documents source available. When none of the requested
    sources is available, the web stands in, so a run never starts with no source at all; the
    caller sees the missing ones named.
    """
    available = available_sources()
    if options.documents and "documents" not in available:
        available = [name for name in SOURCE_TOOLS if name in {*available, "documents"}]  # type: ignore[misc]
    requested = options.sources
    if requested is None:
        return available, []
    usable = [name for name in available if name in requested]
    missing = [name for name in requested if name not in available]
    return usable or ["web"], missing


def documents_description(options: ResearchOptions) -> str:
    """What the documents source holds, for the router's question and the agent's prompt."""
    if not options.documents:
        return PROJECT_DOCUMENTS
    return "the documents the user provided: " + ", ".join(options.documents)
