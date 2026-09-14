from langsmith.anonymizer import SECRET_PLACEHOLDER

from agentlab.utils.secret_redaction_util import (
    EMAIL_PLACEHOLDER,
    make_trace_anonymizer,
    mask_for_trace,
    redact_secrets,
)

FAKE_OPENAI_KEY = "sk-proj-" + "a1B2c3D4" * 4
VALID_TEST_CARD = "4242 4242 4242 4242"


def test_ordinary_text_is_untouched():
    text = "I prefer short answers and work out on Mondays."

    assert redact_secrets(text) == (text, 0)


def test_provider_key_is_redacted_and_counted():
    redacted, found = redact_secrets(f"my key is {FAKE_OPENAI_KEY}, keep it")

    assert redacted == f"my key is {SECRET_PLACEHOLDER}, keep it"
    assert found == 1


def test_password_assignment_keeps_the_name_and_hides_the_value():
    redacted, found = redact_secrets("wifi password=hunter2secret")

    assert redacted == f"wifi password={SECRET_PLACEHOLDER}"
    assert found == 1


def test_card_number_is_redacted_only_when_it_passes_luhn():
    redacted, found = redact_secrets(f"card {VALID_TEST_CARD}, not 4242 4242 4242 4241")

    assert redacted == f"card {SECRET_PLACEHOLDER}, not 4242 4242 4242 4241"
    assert found == 1


def test_trace_view_masks_emails_but_input_redaction_keeps_them():
    text = f"mail me at sam@example.com with {FAKE_OPENAI_KEY}"

    assert mask_for_trace(text) == f"mail me at {EMAIL_PLACEHOLDER} with {SECRET_PLACEHOLDER}"
    assert "sam@example.com" in redact_secrets(text)[0]


def test_trace_anonymizer_reaches_nested_message_payloads():
    payload = {
        "messages": [
            {"content": "hi", "tool_calls": [{"args": {"text": f"key {FAKE_OPENAI_KEY}"}}]},
        ]
    }

    masked = make_trace_anonymizer()(payload)

    assert masked["messages"][0]["tool_calls"][0]["args"]["text"] == f"key {SECRET_PLACEHOLDER}"
