"""LLM model instance definitions.

Centralises all model instantiation so the rest of the codebase
imports ready-to-use model objects rather than constructing them inline.
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# ── Google Gemini ──────────────────────────────────────────────────────────

lite_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0,
    top_p=0.95,
)

flash_model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0,
    top_p=0.95,
)

pro_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro",
    temperature=0,
    top_p=0.95,
)

# ── Anthropic ──────────────────────────────────────────────────────────────

haiku_model = init_chat_model("anthropic:claude-haiku-4-5")

sonnet_model = init_chat_model("anthropic:claude-sonnet-5")
