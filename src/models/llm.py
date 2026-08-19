"""LLM model instance definitions.

Centralises all model instantiation so the rest of the codebase
imports ready-to-use model objects rather than constructing them inline.
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
<<<<<<< HEAD
=======

>>>>>>> ac268283fa2050850887180009b388e00afa28e8

load_dotenv()


# ── Google Gemini ─────────────────────────────────────────────────


lite_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0,
    top_p=0.95,
)


flash_model = ChatGoogleGenerativeAI(
    model="gemini-3.7-flash",
    temperature=0,
    top_p=0.95,
)


pro_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro",
    temperature=0,
    top_p=0.95,
)

<<<<<<< HEAD
# ── GapGPT (OpenAI-compatible proxy, used as fallback route) ────────────

luna_model = ChatOpenAI(
    model="gpt-5.6-luna",
    base_url="https://api.gapgpt.app/v1",
    api_key=os.getenv("GAPGPT_API_KEY"),
    temperature=0,
)

terra_model = ChatOpenAI(
    model="gpt-5.6-terra",
    base_url="https://api.gapgpt.app/v1",
=======

# ── GapGPT (OpenAI-compatible proxy, used as fallback route) ─────────


luna_model = ChatOpenAI(
    model="gpt-5.6-luna",
    base_url=os.getenv("GAPGPT_BASE_URL"),
    api_key=os.getenv("GAPGPT_API_KEY"),
    temperature=0,
)


terra_model = ChatOpenAI(
    model="gpt-5.6-luna",
    base_url=os.getenv("GAPGPT_BASE_URL"),
>>>>>>> ac268283fa2050850887180009b388e00afa28e8
    api_key=os.getenv("GAPGPT_API_KEY"),
    temperature=0,
)
