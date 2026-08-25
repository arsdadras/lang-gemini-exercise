---
  name: retrieval-strategy
  description: Decision policy for choosing between RAG (rag_subagent) and direct filesystem
  tools when answering a question about content in this project's document/code corpus.
  ---

  # Retrieval Strategy

  ## When to Use

  Use this skill whenever you need to answer a question about the *content* of a
  document, note, or code file in this project — before deciding whether to call
  `rag_subagent` or read the file directly with filesystem tools
  (`glob`/`ls`/`grep`/`read_file`).

  ## Decision Policy

  1. **Short file, or the file's exact structure/known content is needed** (e.g. "show me
     the imports in `foo.py`", a file you already know the path of and just need to read) →
     use filesystem tools directly. It fits in context; no retrieval overhead needed.

  2. **A targeted question about content buried somewhere in a large, already-indexed
     corpus** (e.g. "what does the retrieval index module do?") → delegate to `rag_subagent`.
     It embeds the question and retrieves only the relevant chunks — much cheaper and more
     reliable than scanning a large corpus sequentially with filesystem tools.

  3. **Holistic understanding of one large document/file** (not a single targeted fact, but
     synthesis across the whole thing) → prefer reading the full file directly if it fits the
     context window. RAG's chunking can miss connections between distant sections that don't
     look semantically similar to each other even though they're related.

  4. **Large document AND a holistic/synthesis question AND context-window or cost is a real
     constraint** → hybrid "retrieve then read": use `rag_subagent` first as a cheap filter to
     find which section(s) are relevant, then read that narrowed section in full for the
     actual reasoning. Don't try to answer from tiny RAG chunks alone in this case.

  ## Do Not

  - Do not use filesystem tools to search for content across a large, already-indexed corpus
    when `rag_subagent` is available — it wastes tool calls and tokens scanning sequentially.
  - Do not assume RAG alone is sufficient for questions that need cross-section synthesis over
    a document that fits in the context window — prefer a full read for those.
