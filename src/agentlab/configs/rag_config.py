"""Configuration constants for the P2 RAG graph and its document index."""

MAX_RETRIES: int = 2

COLLECTION_NAME: str = "repo_corpus"
RETRIEVER_TOP_K: int = 3

# Corpus paths, relative to the project root.
DOC_FILES: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "offices/lead/ROADMAP.md",
    "offices/mentor/STATE.md",
)
CODE_GLOB: str = "src/**/*.py"

# Embed in paced batches. Sized for Gemini's former free quota (100 requests/minute); the
# embedding model now runs through GapGPT, whose limits haven't been measured.
EMBED_BATCH_SIZE: int = 20
EMBED_BATCH_DELAY_SECONDS: int = 15
