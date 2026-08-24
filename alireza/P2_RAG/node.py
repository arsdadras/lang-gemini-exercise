from .index import get_retriever
from .prompt import grade_prompt, generate_prompt
from .schema import RAGStateAlireza, GradeDocument
from .models import gemini_flash


def retriever_node(state: RAGStateAlireza) -> dict:
    retriever = get_retriever()
    docs = retriever.invoke(state["question"])
    return {"documents": docs}


def judge_node(state: RAGStateAlireza) -> dict:
    llm = gemini_flash.with_structured_output(GradeDocument)
    prompt = grade_prompt
    chain = prompt | llm

    relevant = [
        doc
        for doc in state["documents"]
        if chain.invoke(
            {"question": state["question"], "document": doc.page_content}
        ).binary_score
        == "Yes"
    ]
    return {"documents": relevant}
