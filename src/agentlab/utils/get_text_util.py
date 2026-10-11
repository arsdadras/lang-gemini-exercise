"""Text extraction helpers for LangChain message objects."""

from langchain_core.messages import BaseMessage


def get_text(message: BaseMessage) -> str:
    """Extract the plain-text content from any LangChain message.

    Handles both the simple ``str`` case and the list-of-content-blocks
    format returned by some providers (notably Gemini-3.x).
    """
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part["text"]
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return str(content)
