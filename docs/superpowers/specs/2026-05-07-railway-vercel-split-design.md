# Design: Railway (backend) + Vercel (frontend) split

**Date:** 2026-05-07  
**Status:** Approved

## Problem

The current repo attempts to run a FastAPI + pandas Python backend as a Vercel serverless function. This cannot work because:

- `pandas` + `numpy` exceed Vercel's ~50 MB compressed function size limit
- The in-memory `DocumentCache` and SlowAPI rate limiter rely on shared process state, which is lost between serverless invocations
- The `api/index.py` + `vercel.json` rewrite approach was never functional

## Solution

Split into two deployments:

- **Vercel** — serves `public/index.html` as a static site (zero build step)
- **Railway** — runs the FastAPI process persistently

The frontend calls the Railway API directly from the browser. CORS is already configured in `main.py` (`allow_origins=["*"]`).

## Repository structure after changes

```
public/
  index.html          ← Vercel static deploy (API_BASE updated to Railway URL)

main.py               ← Railway: FastAPI app
cache.py              ← Railway: in-memory document cache
converter.py          ← Railway: DataFrame → Markdown
requirements.txt      ← Railway: Python deps (rdflib + SPARQLWrapper removed)
Procfile              ← Railway: startup command
vendor/eurlex/        ← Railway: vendored HTML fetcher + parser
  public.py           ← trimmed: SPARQL imports removed

DELETED:
  api/index.py        ← dead code from broken Vercel setup
  frontend.html       ← stale root-level duplicate of public/index.html
```

## Changes by file

### New: `Procfile`

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Railway injects `$PORT`. No other Railway-specific config needed — it auto-detects Python via `requirements.txt`.

### Modified: `public/index.html`

Change one line (after Railway URL is known from first deploy):

```js
// Before:
const API_BASE = window.location.protocol === 'file:' ? 'http://localhost:8001' : '';

// After:
const API_BASE = 'https://<your-railway-url>.up.railway.app';
```

### Modified: `vercel.json`

```json
{ "outputDirectory": "public" }
```

Remove all rewrite rules. Vercel only serves static files.

### Modified: `.vercelignore`

Add Python backend files so Vercel ignores them:

```
.venv/
**/__pycache__/
*.pyc
main.py
cache.py
converter.py
api/
vendor/
requirements.txt
Procfile
```

### Modified: `requirements.txt`

Remove unused packages:

```
# REMOVE:
rdflib~=7.6.0
SPARQLWrapper~=2.0.0
```

These are imported by `vendor/eurlex/public.py` at startup but never called by any route. Removing them saves ~9 MB from the installed package set and reduces cold start time.

### Modified: `vendor/eurlex/public.py`

Remove the SPARQL-related imports and `__all__` entries:

```python
# REMOVE these lines:
import rdflib
from SPARQLWrapper import JSON, SPARQLWrapper
from eurlex.sparql import (
    convert_sparql_output_to_dataframe,
    get_celex_dataframe,
    get_documents,
    get_regulations,
    guess_celex_ids_via_eurlex,
    prepend_prefixes,
    run_query,
)
```

And remove the corresponding entries from `__all__`. `sparql.py` itself stays in the vendor untouched — it just won't be imported at startup.

## What stays the same

- `main.py` — no changes to routes, rate limiting, or CORS
- `cache.py` — ThreadLock-based cache works correctly on Railway (persistent process)
- `converter.py` — no changes
- `vendor/eurlex/` — all files kept; only `public.py` trimmed

## Railway setup (for first-time users)

1. Create account at railway.app
2. New Project → Deploy from GitHub repo
3. Railway auto-detects Python and installs `requirements.txt`
4. Set start command via `Procfile` (already in repo after this change)
5. Railway assigns a domain — copy it into `public/index.html` as `API_BASE`
6. Redeploy Vercel (or it auto-deploys on push)

## Out of scope

- Persistent caching across Railway restarts (in-memory cache resets on redeploy; acceptable for immutable EU law documents)
- Authentication
- Custom domains
