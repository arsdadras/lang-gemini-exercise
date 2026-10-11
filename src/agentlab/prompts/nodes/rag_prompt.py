from langchain_core.prompts import ChatPromptTemplate

GRADE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You grade whether a retrieved chunk is relevant to a user question. "
                "Give a binary score 'yes' or 'no'. Be lenient — 'yes' if the chunk "
                "contains any information that could help answer the question."
            ),
        ),
        (
            "human",
            "Question: {question}\n\nChunk:\n{chunk}",
        ),
    ],
)


GENERATE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Answer the question using only the provided context. If the context "
                "doesn't contain the answer, say you don't know. Cite the source file "
                "for each claim using the chunk's 'source' metadata."
            ),
        ),
        (
            "human",
            "Question: {question}\n\nContext:\n{context}",
        ),
    ],
)


REWRITE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You rewrite search queries for a vector-retrieval system. The previous "
                "query returned no relevant chunks. Produce a single improved search "
                "query \u2014 more specific, or using different terminology \u2014 that is "
                "more likely to match relevant chunks. Return only the rewritten query, "
                "nothing else."
            ),
        ),
        (
            "human",
            "Original question: {question}\n\nPrevious search query: {search_query}",
        ),
    ],
)


HALLUCINATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You check whether a generated answer is fully grounded in the provided "
                "context — every claim in the answer must be supported by the context. "
                "Give a binary score 'yes' or 'no'. Be strict."
            ),
        ),
        (
            "human",
            "Context:\n{context}\n\nGenerated answer:\n{answer}",
        ),
    ],
)


GENERATE_FROM_WEB_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Answer the question using only the provided web search results. The "
                "local corpus had nothing relevant, so mention that this answer "
                "comes from the web instead. Cite the source URL for each claim."
            ),
        ),
        (
            "human",
            "Question: {question}\n\nWeb results:\n{context}",
        ),
    ],
)
