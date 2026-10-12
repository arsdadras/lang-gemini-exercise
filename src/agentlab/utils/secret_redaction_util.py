"""Fixed-format secret detection, shared by every place a secret can enter or leave the assistant.

One rule set, several enforcement points: the app redacts user input before the agent sees
it, and the LangSmith client masks traces before upload. The rules are LangSmith's curated
``DEFAULT_SECRET_RULES`` (provider keys, tokens, private keys, ``password=...`` pairs) plus
LangChain's Luhn-checked credit card detector.
"""

from typing import Any

import langsmith
from langchain.agents.middleware import PIIMiddleware
from langchain.agents.middleware.pii import PIIMatch, detect_credit_card, detect_email
from langsmith import Client
from langsmith.anonymizer import (
    DEFAULT_SECRET_RULES,
    SECRET_PLACEHOLDER,
    create_anonymizer,
)

EMAIL_PLACEHOLDER = "[EMAIL]"
_TRACE_MAX_DEPTH = 24

# Personal data that user context or external tool results may hold and that must be
# redacted before an outbound model sees them.
PERSONAL_DATA_TYPES: tuple[str, ...] = ("email", "credit_card", "ip")


def _replace_matches(text: str, matches: list[PIIMatch], placeholder: str) -> str:
    for match in sorted(matches, key=lambda m: m["start"], reverse=True):
        text = text[: match["start"]] + placeholder + text[match["end"] :]
    return text


def redact_secrets(text: str) -> tuple[str, int]:
    """Replace every detected secret with a placeholder; return the text and how many were found."""
    found = 0
    for rule in DEFAULT_SECRET_RULES:
        text, count = rule["pattern"].subn(rule["replace"], text)
        found += count
    cards = detect_credit_card(text)
    return _replace_matches(text, cards, SECRET_PLACEHOLDER), found + len(cards)


def personal_data_redaction() -> list[PIIMiddleware]:
    """Redact personal data (email, credit card, IP) from tool results before the model reads them."""
    return [
        PIIMiddleware(
            kind,
            strategy="redact",
            apply_to_input=False,
            apply_to_tool_results=True,
        )
        for kind in PERSONAL_DATA_TYPES
    ]


def mask_for_trace(text: str, _path: list[str | int] | None = None) -> str:
    """Trace view of ``text``: secrets redacted and email addresses masked."""
    redacted, _ = redact_secrets(text)
    return _replace_matches(redacted, detect_email(redacted), EMAIL_PLACEHOLDER)


def make_trace_anonymizer() -> Any:
    """Anonymizer that applies ``mask_for_trace`` to every string in a traced payload."""
    return create_anonymizer(mask_for_trace, max_depth=_TRACE_MAX_DEPTH)


def make_trace_masking_client() -> Client:
    """LangSmith client that masks run inputs, outputs, and metadata before upload."""
    return Client(anonymizer=make_trace_anonymizer())


def configure_trace_masking() -> None:
    """Configure LangSmith globally with the repo's secret- and email-masking client."""
    langsmith.configure(client=make_trace_masking_client())
