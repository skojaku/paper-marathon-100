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

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "site"
SITE_TITLE = "Paper Marathon 100"
TAGLINE = "Agentic AI reading group"

NAV = [("index.html", "Search"), ("weeks.html", "Weeks"), ("papers.html", "Papers"),
       ("about.html", "About"), ("method.html", "Method")]


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


def badge(count):
    count = max(0, min(count, 100))
    return f"{count}/100", f"#A100{count:02X}"


def page(name, title, body, depth, count, scripts=""):
    root = "../" * depth
    label, color = badge(count)
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
<style>:root{{--progress:{color}}}</style>
</head>
<body>
<header class="top">
  <a class="brand" href="{root}index.html"><span class="badge" title="{count} of 100 papers read">{label}</span>
    <span class="brand-text"><strong>{SITE_TITLE}</strong><small>{TAGLINE}</small></span></a>
  <nav>{nav}</nav>
</header>
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
    count = sum(len(w.get("papers") or []) for w in weeks)

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
            page("weeks.html", w["title"], body, 1, count))
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
<div class="cards">{cards}</div>""", 0, count))

    (OUT / "data/weeks.json").write_text(json.dumps(
        [{"slug": w["slug"], "week": w["week"], "date": str(w["date"]), "title": w["title"],
          "summary": w.get("summary", ""), "text": w["text"]} for w in weeks],
        ensure_ascii=False, separators=(",", ":")))

    # ---- search / papers
    n_ven = len({p["venue"] for p in papers})
    search_scripts = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/minisearch/7.1.0/umd/index.min.js"></script>'
                      '<script src="{r}assets/app.js"></script>')
    (OUT / "index.html").write_text(page("index.html", "Search", f"""
<section class="hero">
  <h1>Read a hundred papers, one week at a time.</h1>
  <p class="lead">Search the papers we are reading and what we wrote about them.</p>
  <input id="q" class="search" type="search" placeholder="Search papers, summaries, questions…" autofocus autocomplete="off">
  <p class="muted stat">{len(papers):,} multi-agent LLM papers from {n_ven} venues, 2023–2026 · {len(weeks)} week{'s' if len(weeks) != 1 else ''} written up</p>
</section>
<div id="results" data-mode="all"></div>""", 0, count, search_scripts.format(r="")))

    (OUT / "papers.html").write_text(page("papers.html", "Papers", f"""
<h1>Papers</h1>
<p class="lead">The candidate list for the first theme, multi-agent systems. {len(papers):,} papers; tags are LLM-generated.</p>
<input id="q" class="search" type="search" placeholder="Filter by title, abstract or tag…" autocomplete="off">
<div id="filters" class="filters"></div>
<div id="results" data-mode="papers"></div>""", 0, count, search_scripts.format(r="")))

    # ---- static pages
    for path in sorted((ROOT / "pages").glob("*.md")):
        meta, body = front(path)
        title = meta.get("title", path.stem.title())
        body = body.replace("{{N_PAPERS}}", f"{len(papers):,}").replace("{{N_VENUES}}", str(n_ven))
        (OUT / f"{path.stem}.html").write_text(
            page(f"{path.stem}.html", title, f'<article class="prose">{md(body)}</article>', 0, count))

    print(f"built {len(papers)} papers, {len(weeks)} weeks, badge {badge(count)[0]} -> {OUT}")


if __name__ == "__main__":
    main()
