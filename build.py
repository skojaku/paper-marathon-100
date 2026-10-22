"""Build the Paper Marathon 100 static site into ./site.

    uv run --with markdown --with pyyaml build.py

Inputs:  data/papers.json, weeks/*.md, pages/*.md, assets/
Output:  site/ (what GitHub Pages serves)
"""
import html
import json
import re
import shutil
from pathlib import Path

import markdown
import yaml

from mascot import crowd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "site"
SITE_TITLE = "Paper Marathon 100"
TAGLINE = "Agentic AI reading group"

READ = []  # (paper title, week slug) in reading order; one character each

NAV = [("index.html", "Papers"), ("weeks.html", "Weeks"), ("about.html", "About"), ("method.html", "Method")]


def md(text):
    return markdown.markdown(text, extensions=["extra", "sane_lists", "toc"])


def front(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    meta = yaml.safe_load(m.group(1)) if m else {}
    return meta or {}, (m.group(2) if m else text)


def plain(text):
    text = re.sub(r"[#*_`>\[\]()|-]", " ", text)
    return " ".join(text.split())


def page(name, title, body, depth, scripts=""):
    root = "../" * depth
    nav = "".join(
        f'<a href="{root}{href}"{" aria-current=page" if href == name else ""}>{text}</a>'
        for href, text in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {SITE_TITLE}</title>
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="{root}index.html">
    <span class="brand-text"><strong>{SITE_TITLE}</strong><small>{TAGLINE}</small></span></a>
  <nav>{nav}</nav>
</header>
{crowd(READ, root)}
<main>
{body}
</main>
<footer>Summaries and questions are written by the participants each week; tags on the paper list are LLM-generated (see <a href="{root}method.html">Method</a>).</footer>
{scripts}
</body>
</html>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "weeks").mkdir(parents=True)
    (OUT / "data").mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")

    papers = json.loads((ROOT / "data/papers.json").read_text())
    (OUT / "data/papers.json").write_text(json.dumps(papers, ensure_ascii=False, separators=(",", ":")))

    # ---- weeks
    weeks = []
    for path in sorted((ROOT / "weeks").glob("*.md")):
        if path.name.startswith("_"):
            continue
        meta, body = front(path)
        meta["slug"] = path.stem
        meta["body_md"] = body
        weeks.append(meta)
    weeks.sort(key=lambda w: str(w["date"]))
    READ[:] = [(p["title"], w["slug"]) for w in weeks for p in (w.get("papers") or [])]
    count = len(READ)

    for w in weeks:
        rows = ""
        for p in w.get("papers") or []:
            who = f' <span class="muted">· {html.escape(p["presenter"])}</span>' if p.get("presenter") else ""
            title = html.escape(p["title"])
            link = f'<a href="{html.escape(p["url"])}">{title}</a>' if p.get("url") else title
            rows += f"<li>{link}{who}</li>"
        body = f"""<article class="week">
<p class="crumb"><a href="../weeks.html">← All weeks</a></p>
<p class="kicker">Week {w['week']} · {w['date']}</p>
<h1>{html.escape(w['title'])}</h1>
{f'<h2>Papers read</h2><ul class="plain">{rows}</ul>' if rows else ''}
{md(w['body_md'])}
</article>"""
        (OUT / "weeks" / f"{w['slug']}.html").write_text(
            page("weeks.html", w["title"], body, 1))
        w["text"] = plain(w["body_md"])

    cards = ""
    for w in reversed(weeks):
        n = len(w.get("papers") or [])
        cards += f"""<a class="card" href="weeks/{w['slug']}.html">
<span class="kicker">Week {w['week']} · {w['date']}</span>
<h3>{html.escape(w['title'])}</h3>
<p>{html.escape(w.get('summary', ''))}</p>
<span class="muted">{n} paper{'s' if n != 1 else ''}</span></a>"""
    if not cards:
        cards = '<p class="empty">No weeks yet. The first session is on 2026-11-05; each week appears here as a card.</p>'
    (OUT / "weeks.html").write_text(page("weeks.html", "Weeks", f"""
<h1>Weeks</h1>
<p class="lead">One page per meeting: what was read, what we learned, and the questions left open.</p>
<div class="cards">{cards}</div>""", 0))

    (OUT / "data/weeks.json").write_text(json.dumps(
        [{"slug": w["slug"], "week": w["week"], "date": str(w["date"]), "title": w["title"],
          "summary": w.get("summary", ""), "text": w["text"]} for w in weeks],
        ensure_ascii=False, separators=(",", ":")))

    # ---- landing page = the paper list (search covers weeks too)
    scripts = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/minisearch/7.1.0/umd/index.min.js"></script>'
               '<script src="assets/app.js"></script>')
    (OUT / "index.html").write_text(page("index.html", "Papers", """
<h1>Papers</h1>
<p class="lead">Papers on multi-agent systems, with the weekly write-ups. Tags are LLM-generated.</p>
<input id="q" class="search" type="search" placeholder="Search papers and weekly write-ups…" autofocus autocomplete="off">
<div id="filters" class="filters"></div>
<div id="results" data-mode="papers"></div>""", 0, scripts))

    # ---- static pages
    for path in sorted((ROOT / "pages").glob("*.md")):
        meta, body = front(path)
        title = meta.get("title", path.stem.title())
        (OUT / f"{path.stem}.html").write_text(
            page(f"{path.stem}.html", title, f'<article class="prose">{md(body)}</article>', 0))

    print(f"built {len(papers)} papers, {len(weeks)} weeks, {count} read -> {OUT}")


if __name__ == "__main__":
    main()
