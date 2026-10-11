"""Document ingestion and vector retrieval for the P2 RAG agent."""

from .index_retrieval import build_index, get_retriever

__all__ = ["build_index", "get_retriever"]
