from langchain_core.prompts import ChatPromptTemplate


_GROUNDEDNESS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You check whether an AI assistant's final answer is fully grounded in "
            "the provided tool-output context — every claim in the answer must be "
            "supported by the context. Give a binary score 'yes' or 'no'. Be strict.",
        ),
        (
            "human",
            "Tool output context:\n{context}\n\nFinal answer:\n{answer}",
        ),
    ]
)
