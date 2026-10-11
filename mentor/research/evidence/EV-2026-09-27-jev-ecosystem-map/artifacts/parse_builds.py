"""Parse shipwithjev build pages into one JSON dataset (title, summary, category, type,
source, reported cost and latency, and the opening of the page's body text)."""

import html
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
rows = []
for f in sorted((HERE / "builds").glob("*.html")):
    raw = f.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    lines = [ln.strip() for ln in html.unescape(re.sub(r"<[^>]+>", "\n", body)).splitlines()
             if ln.strip()]
    meta = re.search(r'<meta name="description" content="(.*?)"', raw, flags=re.S)
    title = re.search(r"<title>(.*?)</title>", raw, flags=re.S)
    title = html.unescape(title.group(1)).split(" · ")[0].strip() if title else f.stem

    def after(label):
        for i, ln in enumerate(lines):
            if ln == label and i + 1 < len(lines):
                return lines[i + 1]
        return None

    try:
        start = lines.index(title, 10)
    except ValueError:
        start = 0
    rest = lines[start + 1:]
    stop = next((i for i, ln in enumerate(rest) if ln == "Receipts"), len(rest))
    text = " ".join(x for x in rest[:stop] if x not in {"Share", "cost", "time", "-"})
    rows.append({
        "slug": f.stem,
        "title": title,
        "summary": html.unescape(meta.group(1)).strip() if meta else "",
        "category": after("Category"),
        "type": after("Type"),
        "source": after("Source"),
        "author": after("Author"),
        "reported_cost": after("Reported cost"),
        "reported_latency": after("Reported latency"),
        "text": text[:1500],
    })

(HERE / "builds.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False),
                                   encoding="utf-8")
print(len(rows), "builds")
from collections import Counter
print(Counter(r["category"] for r in rows))
print(Counter(r["type"] for r in rows))
print(sum(1 for r in rows if r["reported_cost"] not in (None, "-")), "with reported cost;",
      sum(1 for r in rows if r["reported_latency"] not in (None, "-")), "with reported latency")
