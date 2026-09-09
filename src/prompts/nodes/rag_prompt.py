from langchain_core.prompts import ChatPromptTemplate

_grade_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You grade whether a retrieved document is relevant to a user question. "
                "Give a binary score 'yes' or 'no'. Be lenient — 'yes' if the document "
                "contains any information that could help answer the question."
            ),
        ),
        (
            "human",
            "Question: {question}\n\nDocument:\n{document}",
        ),
    ]
)


_generate_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Answer the question using only the provided context. If the context "
                "doesn't contain the answer, say you don't know. Cite the source file "
                "for each claim using the document's 'source' metadata."
            ),
        ),
        (
            "human",
            "Question: {question}\n\nContext:\n{context}",
        ),
    ]
)


_rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You rewrite search queries for a vector-retrieval system. The previous "
                "query returned no relevant documents. Produce a single improved search "
                "query \u2014 more specific, or using different terminology \u2014 that is "
                "more likely to match relevant documents. Return only the rewritten query, "
                "nothing else."
            ),
        ),
        (
            "human",
            "Original question: {question}\n\nPrevious search query: {search_query}",
        ),
    ]
)


_hallucination_prompt = ChatPromptTemplate.from_messages(
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
            "Context:\n{context}\n\nGenerated answer:\n{generation}",
        ),
    ]
)


_generate_from_web_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Answer the question using only the provided web search results. The "
                "local document corpus had nothing relevant, so mention that this answer "
                "comes from the web instead. Cite the source URL for each claim."
            ),
        ),
        (
            "human",
            "Question: {question}\n\nWeb results:\n{context}",
        ),
    ]
)
