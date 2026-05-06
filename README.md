# eurlex-to-md

Converts EU legal documents from EUR-Lex into clean Markdown. Paste a CELEX ID or EUR-Lex URL and get back structured Markdown ready to read, download, or process further.

## What it does

Given a CELEX ID (e.g. `32024R1689` for the EU AI Act), it fetches the document from the CELLAR API (the Publications Office linked-data endpoint), parses the HTML, and returns:

- Structured Markdown with sections, articles, and paragraphs
- Document title and article count
- In-memory cache so repeat lookups are instant

A browser-based frontend (`public/index.html`) lets you paste EUR-Lex links directly and preview/download the result.

## Setup

Requires Python 3.12+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
.venv/bin/uvicorn main:app --reload --port 8001
```

Then open `public/index.html` in your browser (just double-click the file).

## API

```
GET /generate/{celex_id}
```

Returns JSON:

```json
{
  "celex_id": "32024R1689",
  "title": "REGULATION (EU) 2024/1689 ...",
  "article_count": 113,
  "markdown": "# REGULATION ...\n\n## Section ...\n\n### Article 1 ..."
}
```

```
GET /health
```

Returns `{"status": "ok", "cached_documents": N}`.

**Error codes:** `404` document not found, `503` CELLAR API unreachable, `429` rate limited (10 req/min per IP).

## Quick test

```bash
curl http://localhost:8001/health
curl http://localhost:8001/generate/32024R1689
```

## Project structure

```
main.py           FastAPI app, rate limiting, two routes
converter.py      DataFrame → Markdown conversion
cache.py          Thread-safe in-memory cache
api/index.py      Vercel serverless entry point
public/index.html EUR-Lex-styled browser UI
vendor/eurlex/    Vendored eurlex package (see below)
vercel.json       Vercel routing config
```

## Credits

EUR-Lex fetching and HTML parsing are handled by the [eurlex](https://github.com/kevin91nl/eurlex) library by [K.M.J. Jacobs](https://github.com/kevin91nl), vendored here under its [MIT license](vendor/eurlex/LICENSE).
