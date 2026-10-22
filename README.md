# Paper Marathon 100 — agentic AI reading group site

Static site (GitHub Pages). Search runs in the browser (MiniSearch); no server.

- `data/papers.json` — paper list (`scripts/prepare_papers.py` trims the export from aster's `teams4industry/exps/2026-1019-mas-paper-classification`)
- `weeks/*.md` — one file per meeting (copy `weeks/_template.md`); the runner on the map advances one stop per `papers:` entry (`worldmap.py` draws the map, `assets/map.js` moves the runner)
- `pages/*.md` — About, Method
- `build.py` — `uv run --with markdown --with pyyaml build.py` writes `site/`; preview with `python3 -m http.server -d site`
- `.github/workflows/pages.yml` — builds and deploys on push to `main` (repo Settings → Pages → Source: GitHub Actions)
