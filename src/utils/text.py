"""Text extraction helpers for LangChain message objects."""

from langchain.messages import AIMessage


def get_text(message: AIMessage) -> str:
    """Extract the plain-text content from an AIMessage.

    Handles both the simple ``str`` case and the list-of-content-blocks
    format returned by some providers.
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
