"""Configuration constants for the P2 RAG graph and its document index."""

MAX_RETRIES: int = 2

COLLECTION_NAME: str = "repo_corpus"
EMBEDDING_MODEL: str = "gemini-embedding-2-preview"
RETRIEVER_TOP_K: int = 3

# Corpus paths, relative to the project root.
DOC_FILES: tuple[str, ...] = ("README.md", "AGENTS.md", "docs/ROADMAP.md", "docs/MENTOR_HANDOFF.md")
CODE_GLOB: str = "src/**/*.py"

# Gemini's free embedding quota is 100 requests/minute, so embed in paced batches.
EMBED_BATCH_SIZE: int = 20
EMBED_BATCH_DELAY_SECONDS: int = 15
