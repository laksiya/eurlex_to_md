# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

FastAPI backend that converts EU legal documents (EUR-Lex) to Markdown. Given a CELEX ID (e.g., `32024R1689` for the EU AI Act), it fetches from the CELLAR API (Publications Office's linked-data endpoint), parses HTML, and returns structured Markdown.

## Setup

Python 3.12+. All dependencies are in `requirements.txt` — no sibling directory needed.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
.venv/bin/uvicorn main:app --reload --port 8001
```

Test with:
```bash
curl http://localhost:8001/health
curl http://localhost:8001/generate/32024R1689
```

## Architecture

Three modules with clear separation:

- **[main.py](main.py)** — FastAPI app, rate limiting (SlowAPI, 10 req/min per IP), two routes: `GET /generate/{celex_id}` and `GET /health`. Calls `get_html_by_celex_id()` and `parse_html()` from the vendored `eurlex` package.
- **[converter.py](converter.py)** — Converts the Pandas DataFrame from `parse_html()` into Markdown. Groups content by section → article → paragraph. Notes become blockquotes; signatories are skipped; article references render as indented lists.
- **[cache.py](cache.py)** — Thread-safe in-memory dict cache keyed by CELEX ID. Documents cached indefinitely (they're immutable EU law).
- **[vendor/eurlex/](vendor/eurlex/)** — Vendored copy of [kevin91nl/eurlex](https://github.com/kevin91nl/eurlex) (MIT). Owns CELLAR API fetching and HTML parsing. Added to `sys.path` at startup in `main.py` so its internal imports resolve unchanged.

This repo only handles the HTTP layer and Markdown conversion; the CELLAR API fetching and HTML parsing belong to the vendored package.

## API Response Shape

```json
{
  "celex_id": "32024R1689",
  "title": "REGULATION (EU) 2024/1689 ...",
  "article_count": 113,
  "markdown": "# REGULATION ...\n\n## Section ...\n\n### Article 1 ..."
}
```

Errors: 404 if document not found/unparseable, 503 if CELLAR API unreachable, 429 if rate limited.
