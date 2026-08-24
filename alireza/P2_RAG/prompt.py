from langchain_core.prompts.chat import ChatPromptTemplate

grade_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You grade whether a retrieved document is relevant to a user question. "
            "Give a binary score 'yes' or 'no'. Be lenient — 'yes' if the document "
            "contains any information that could help answer the question.",
        ),
        ("human", "User Query: {question}\n\nRetrieved Document:\n{document}"),
    ]
)


generate_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You generate a concise, grounded answer based on retrieved documents."
            "If the documents don't contain sufficient information to answer, say you can't answer based on existed data."
            "Cite the source file for each claim using the document's source metadata.",
        ),
        ("human", "User Query: {question}\n\nContext:\n{context}"),
    ]
)
