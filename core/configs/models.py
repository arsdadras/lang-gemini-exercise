"""LLM model registry configuration.

Each role maps to `init_chat_model(...)` kwargs — swap the provider/model
for a role here, and every node/agent using that role picks it up.
`FALLBACK_CHAIN` is tried, in order, whenever a primary call raises
(rate limits, transient provider errors, etc.) — see `models.registry`.
"""

import os

MODEL_REGISTRY = {
    "lite": {
        "model": "gemini-3.5-flash-lite",
        "model_provider": "google_genai",
        "temperature": 0,
        "top_p": 0.95,
    },
    "flash": {
        "model": "gemini-3.7-flash",
        "model_provider": "google_genai",
        "temperature": 0,
        "top_p": 0.95,
    },
    "pro": {
        "model": "gemini-3.1-pro",
        "model_provider": "google_genai",
        "temperature": 0,
        "top_p": 0.95,
    },
}

DEFAULT_ROLE = "lite"

# GapGPT (OpenAI-compatible proxy) — tried in order when a primary call raises.
FALLBACK_CHAIN = [
    {
        "model": "gpt-5.6-luna",
        "model_provider": "openai",
        "base_url": os.getenv("GAPGPT_BASE_URL"),
        "api_key": os.getenv("GAPGPT_API_KEY"),
        "temperature": 0,
    },
    {
        "model": "gpt-5.6-terra",
        "model_provider": "openai",
        "base_url": os.getenv("GAPGPT_BASE_URL"),
        "api_key": os.getenv("GAPGPT_API_KEY"),
        "temperature": 0,
    },
]
