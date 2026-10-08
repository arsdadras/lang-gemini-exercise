"""``search_documents``: the documents source, searched like P2's corpus (R1 topic 3).

By default it searches this project's own docs and code through P2's index; a run whose caller
gave it files searches those instead (``retrieval/documents_retrieval.py``). Chunks that come
from the same file are joined into one document, referenced as ``corpus://<path>``, of kind
``corpus``, so the claim check judges a claim against everything the agent read of that file.

The retriever is built on the first call, not with the tool, so building an agent opens no
index and embeds nothing; a missing index or an embedding failure goes back to the model as
text.
"""

from collections.abc import Callable
from typing import Any

from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import StructuredTool, ToolException

from agentlab.schemas.output.research_output_schema import SourceDocument
from agentlab.tools.research_source_tool import as_artifact, format_documents
from agentlab.utils.failure_util import failure_kind

DOCUMENTS_SEARCH_TOOL_NAME = "search_documents"
CORPUS_SCHEME = "corpus://"


def make_documents_search_tool(
    retriever_factory: Callable[[], BaseRetriever], description: str
) -> StructuredTool:
    """Build the documents search tool over the retriever ``retriever_factory`` opens.

    ``description`` says what the documents hold (``documents_description``).
    """
    retriever: BaseRetriever | None = None

    def search_documents(query: str) -> tuple[str, list[dict[str, Any]]]:
        nonlocal retriever
        try:
            retriever = retriever or retriever_factory()
            chunks = retriever.invoke(query)
        except FileNotFoundError as error:
            raise ToolException(str(error)) from error
        except Exception as error:
            if failure_kind(error) is None:
                raise
            msg = f"The document search failed: {error}"
            raise ToolException(msg) from error
        texts: dict[str, list[str]] = {}
        for chunk in chunks:
            path = chunk.metadata.get("source", "unknown")
            texts.setdefault(path, []).append(chunk.page_content)
        documents = [
            SourceDocument(
                url=f"{CORPUS_SCHEME}{path}",
                title=path,
                kind="corpus",
                text="\n...\n".join(parts),
            )
            for path, parts in texts.items()
        ]
        if not documents:
            return "Nothing in the documents matches. Try a different query.", []
        return format_documents(documents), as_artifact(documents)

    return StructuredTool.from_function(
        search_documents,
        name=DOCUMENTS_SEARCH_TOOL_NAME,
        description=(
            f"Search {description}. Use it for questions about them; cite a file by the "
            "corpus:// reference it returns."
        ),
        handle_tool_error=True,
        response_format="content_and_artifact",
    )
