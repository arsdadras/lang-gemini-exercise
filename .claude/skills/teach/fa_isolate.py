"""Turn a Persian lesson draft into text that keeps its order when Persian and English mix.

Write the draft with every Latin run (identifier, code span, English term, abbreviation)
between ``<<`` and ``>>``. This script swaps those markers for the invisible Unicode
isolates LRI (U+2066) and PDI (U+2069), and checks the draft against persian.md.

    python .claude/skills/teach/fa_isolate.py draft.txt          # or text on stdin
    python .claude/skills/teach/fa_isolate.py draft.txt --rtl    # also wrap each paragraph in RLI..PDI

Fenced code blocks are left alone. Problems go to stderr; a bad marker exits with 1.
"""

import re
import sys

LRI, RLI, PDI = "⁦", "⁧", "⁩"
FENCE = re.compile(r"(```.*?```)", re.S)
MARK = re.compile(r"<<(.+?)>>", re.S)
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
        return MARK.sub(lambda m: LRI + m.group(1) + PDI, part)

    parts = FENCE.split(text)
    converted = "".join(p if p.startswith("```") else wrap(p) for p in parts)
    if "<<" in converted or ">>" in converted:
        errors.append("unbalanced or nested << >> markers")
    if rtl:
        converted = "\n\n".join(
            block if block.startswith("```") else RLI + block + PDI
            for block in converted.split("\n\n")
        )
    return converted, errors, warnings


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.stdout.reconfigure(encoding="utf-8")
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
