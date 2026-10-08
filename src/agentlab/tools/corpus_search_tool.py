"""``search_corpus``: this project's own docs and code, through P2's index (R1 topic 3).

The private source: internal knowledge a web search can't reach. Chunks that come from the same
file are joined into one document, referenced as ``corpus://<path>``, of kind ``corpus``, so the
claim check judges a claim against everything the agent read of that file.

The retriever is built on the first call, not with the tool, so building an agent opens no
index; a missing index or an embedding failure goes back to the model as text.
"""

from collections.abc import Callable
from typing import Any

from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import StructuredTool, ToolException

from agentlab.schemas.output.research_output_schema import SourceDocument
from agentlab.tools.research_source_tool import as_artifact, format_documents
from agentlab.utils.failure_util import failure_kind

CORPUS_SEARCH_TOOL_NAME = "search_corpus"
CORPUS_SCHEME = "corpus://"


def make_corpus_search_tool(
    retriever_factory: Callable[[], BaseRetriever],
) -> StructuredTool:
    """Build the corpus search tool over the retriever ``retriever_factory`` opens."""
    retriever: BaseRetriever | None = None

    def search_corpus(query: str) -> tuple[str, list[dict[str, Any]]]:
        """Search this project's own documentation and source code (agentlab: its design
        decisions, architecture, conventions, and code). Use it for questions about this
        project; cite a file by the corpus:// reference it returns."""
        nonlocal retriever
        try:
            retriever = retriever or retriever_factory()
            chunks = retriever.invoke(query)
        except FileNotFoundError as error:
            raise ToolException(str(error)) from error
        except Exception as error:
            if failure_kind(error) is None:
                raise
            msg = f"The corpus search failed: {error}"
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
            return "Nothing in the corpus matches. Try a different query.", []
        return format_documents(documents), as_artifact(documents)

    return StructuredTool.from_function(
        search_corpus,
        name=CORPUS_SEARCH_TOOL_NAME,
        handle_tool_error=True,
        response_format="content_and_artifact",
    )
