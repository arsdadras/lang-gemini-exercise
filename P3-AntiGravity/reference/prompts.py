"""Reference prompts for P3 Code Review."""
from langchain_core.prompts.chat import ChatPromptTemplate

_REVIEW_SYSTEM = """You are a Principal Software Engineer and Code Reviewer.
Conduct a thorough, rigorous, and actionable code review."""

REVIEW_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _REVIEW_SYSTEM),
    ("human", "Please review the following {language} code:\nFile path: {file_path}\n\n```\n{code}\n```"),
])

_TEST_GEN_SYSTEM = """You are a Senior QA Automation Engineer.
Generate a comprehensive, robust test suite."""

TEST_GEN_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _TEST_GEN_SYSTEM),
    ("human", "Generate a complete {framework} test suite for the following {language} code.\nFile path: {file_path}\n\nSource Code:\n```\n{code}\n```\n\nReview Summary & Findings:\n{review_summary}"),
])
