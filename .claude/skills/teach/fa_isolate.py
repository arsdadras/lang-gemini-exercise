"""Turn a Persian lesson draft into text that keeps its order when Persian and English mix.

Write the draft with every Latin run (identifier, code span, markdown link, English term,
abbreviation) between ``<<`` and ``>>``. This script swaps those markers for the invisible
Unicode isolates ``RLM + LRI`` (U+200F + U+2066) and ``PDI + RLM`` (U+2069 + U+200F), starts and
ends every paragraph with an invisible right-to-left mark (RLM, U+200F), and checks the draft
against persian.md.

    uv run python .agents/skills/teach/fa_isolate.py draft.txt          # or text on stdin
    uv run python .agents/skills/teach/fa_isolate.py draft.txt --rtl    # also wrap each paragraph in RLI..PDI

Fenced code blocks are left alone. Problems go to stderr; a bad marker exits with 1.
"""

import re
import sys
from collections.abc import Callable

LRI, RLI, PDI, RLM = "\u2066", "\u2067", "\u2069", "\u200f"
LEADING_MARKUP = re.compile(r"^\s*(?:#+ |[-*>] |\d+\. )*")
BULLET_OR_NUMBER_LIST = re.compile(r"^\s*(?:[-*] |\d+\. )")
LATIN_START = re.compile(r"[A-Za-z0-9]")
FENCE = re.compile(r"(```.*?```)", re.DOTALL)
MARK = re.compile(r"<<(.+?)>>", re.DOTALL)
LINK_TARGET = re.compile(r"\]\([^)]*\)")
LATIN = re.compile(r"[A-Za-z][A-Za-z0-9_./#-]*")
GLUED = re.compile(r">>[‌ء-ی]")

# Persian renderings of terms that stay English (persian.md, section 2).
TRANSLATED = {
    "بالا می‌آید": "raise",
    "صدا می‌زنیم": "call",
    "صدا می‌زند": "call",
    "صدا بزن": "call",
    "برمی‌گرداند": "return",
    "تصمیم‌گیرنده": "decider",
    "پرتاب": "raise",
    "استثنا": "exception",
    "مجموعه‌داده": "dataset",
    "مجموعه داده": "dataset",
    "برچسب": "label",
    "خطای بیرونی": "external error",
}


def convert(text: str, rtl: bool = False) -> tuple[str, list[str], list[str]]:
    """Return the converted text, the errors, and the warnings."""
    errors: list[str] = []
    warnings: list[str] = []
    prose = FENCE.sub("", text)
    for term, english in TRANSLATED.items():
        if term in prose:
            warnings.append(f"translated term {term!r}: keep it English ({english})")
    for glued in GLUED.finditer(prose):
        start = max(glued.start() - 12, 0)
        warnings.append(
            f"Persian letters glued to a Latin run: ...{prose[start : glued.end() + 4]!r}"
        )
    bare = re.sub(r"https?://\S+", "", LINK_TARGET.sub("", MARK.sub("", prose)))
    naked = sorted(set(LATIN.findall(bare)))
    if naked:
        warnings.append("Latin outside << >>: " + ", ".join(naked))

    def wrap(part: str) -> str:
        return MARK.sub(lambda m: RLM + LRI + m.group(1) + PDI + RLM, part)

    for block in prose.split("\n\n"):
        stripped = block.strip()
        if not stripped:
            continue
        if BULLET_OR_NUMBER_LIST.match(stripped):
            warnings.append(
                f"paragraph uses markdown bullet/numbered list (forbidden in Persian): {stripped[:30]!r}"
            )
        first = LEADING_MARKUP.sub("", stripped)
        if first.startswith("<<") or LATIN_START.match(first):
            warnings.append(f"paragraph starts with a Latin run: {first[:30]!r}")

    parts = FENCE.split(text)
    converted = "".join(p if p.startswith("```") else wrap(p) for p in parts)
    if "<<" in converted or ">>" in converted:
        errors.append("unbalanced or nested << >> markers")
    converted = per_paragraph(converted, start_with_rlm)
    if rtl:
        converted = per_paragraph(converted, lambda block: RLI + block + PDI)
    return converted, errors, warnings


def per_paragraph(text: str, change: Callable[[str], str]) -> str:
    """Apply ``change`` to each prose paragraph; a fenced block stays whole, blank lines and all."""
    out = []
    for part in FENCE.split(text):
        if part.startswith("```"):
            out.append(part)
        else:
            out.append(
                "\n\n".join(change(b) if b.strip() else b for b in part.split("\n\n"))
            )
    return "".join(out)


def start_with_rlm(block: str) -> str:
    """Put an invisible right-to-left mark at the start and end of each paragraph."""
    lead = LEADING_MARKUP.match(block)
    cut = lead.end() if lead else 0
    body = block[cut:]
    if not body.startswith(RLM):
        body = RLM + body
    if not body.endswith(RLM):
        body = body + RLM
    return block[:cut] + body


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if args:
        with open(args[0], encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.read()
    converted, errors, warnings = convert(text, rtl="--rtl" in sys.argv)
    for message in warnings:
        print("warning:", message, file=sys.stderr)
    for message in errors:
        print("error:", message, file=sys.stderr)
    if errors:
        return 1
    print(converted)
    print(f"ok: {converted.count(LRI)} isolates", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
