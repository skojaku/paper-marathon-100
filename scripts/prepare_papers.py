"""Trim the raw export from aster (data/papers_raw.json) to the papers the site shows.

Keeps papers the full-text classification (Argon, codebook v0.8) judged to be multi-agent
LLM systems, and the fields the site needs. Run once when the list is refreshed.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
raw = json.loads((root / "data/papers_raw.json").read_text())
keep = []
for p in raw:
    if not p["eligible"]:
        continue
    keep.append({
        "id": p["id"],
        "title": " ".join(p["title"].split()),
        "venue": p["venue"],
        "year": p["year"],
        "url": p["url"] or (f"https://arxiv.org/abs/{p['arxiv']}" if p["arxiv"] else ""),
        "arxiv": p["arxiv"] or "",
        "abstract": " ".join((p["abstract"] or "").split()),
        "purpose": p["purpose"],
        "relation": p["relation"],
        "structure": p["group_types"] or [],
        "tags": p["constructs"],
    })
keep.sort(key=lambda p: (-p["year"], p["venue"], p["title"].lower()))
(root / "data/papers.json").write_text(json.dumps(keep, ensure_ascii=False, indent=0))
print(len(keep), "papers")
