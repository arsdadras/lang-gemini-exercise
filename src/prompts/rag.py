from langchain_core.prompts import ChatPromptTemplate


_grade_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You grade whether a retrieved document is relevant to a user question. "
            "Give a binary score 'yes' or 'no'. Be lenient — 'yes' if the document "
            "contains any information that could help answer the question.",
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
            "Answer the question using only the provided context. If the context "
            "doesn't contain the answer, say you don't know. Cite the source file "
            "for each claim using the document's 'source' metadata.",
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
            "You rewrite search queries for a vector-retrieval system. The previous "
            "query returned no relevant documents. Produce a single improved search "
            "query \u2014 more specific, or using different terminology \u2014 that is "
            "more likely to match relevant documents. Return only the rewritten query, "
            "nothing else.",
        ),
        (
            "human",
            "Original question: {question}\n\nPrevious search query: {search_query}",
        ),
    ]
)
