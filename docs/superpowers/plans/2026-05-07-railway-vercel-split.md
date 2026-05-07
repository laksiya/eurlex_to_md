# Railway + Vercel Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy the FastAPI backend on Railway and the static frontend on Vercel, replacing the broken attempt to run Python as a Vercel serverless function.

**Architecture:** Railway runs the FastAPI process persistently (in-memory cache and rate limiting work correctly). Vercel serves `public/index.html` as a plain static site. The browser calls the Railway API directly — CORS is already open in `main.py`.

**Tech Stack:** FastAPI + uvicorn on Railway (Python 3.12), static HTML on Vercel, no build step.

---

## Files changed

| File | Action |
|------|--------|
| `api/index.py` | **Delete** — dead code from broken Vercel setup |
| `frontend.html` | **Delete** — stale root-level duplicate of `public/index.html` |
| `Procfile` | **Create** — tells Railway how to start the server |
| `vendor/eurlex/public.py` | **Modify** — remove unused SPARQL imports that load rdflib at startup |
| `requirements.txt` | **Modify** — remove `rdflib` and `SPARQLWrapper` |
| `vercel.json` | **Modify** — strip to static-only config |
| `.vercelignore` | **Modify** — exclude all Python backend files |
| `public/index.html` | **Modify** — point `API_BASE` at Railway URL + fix local dev detection |

---

## Task 1: Delete dead files

**Files:**
- Delete: `api/index.py`
- Delete: `frontend.html`

- [ ] **Step 1: Delete `api/index.py`**

  ```bash
  rm api/index.py
  rmdir api
  ```

- [ ] **Step 2: Delete root-level `frontend.html`**

  ```bash
  rm frontend.html
  ```

- [ ] **Step 3: Verify the app still imports cleanly**

  ```bash
  source .venv/bin/activate
  python -c "from main import app; print('OK')"
  ```

  Expected output: `OK`

- [ ] **Step 4: Commit**

  ```bash
  git add -A
  git commit -m "chore: remove dead api/ folder and stale frontend.html"
  ```

---

## Task 2: Remove unused SPARQL imports from the vendor package

`vendor/eurlex/public.py` currently imports `rdflib` and `SPARQLWrapper` at module load time. Your app never calls any SPARQL function — only `get_html_by_celex_id` and `parse_html` are used. Removing these cuts startup time and dependency weight.

**Files:**
- Modify: `vendor/eurlex/public.py`

- [ ] **Step 1: Replace `vendor/eurlex/public.py` with the trimmed version**

  Full file content after change:

  ```python
  """Central public API surface for the EUR-Lex package.

  This module keeps the package facade easy to scan for new contributors while
  allowing the package root to stay tiny.
  """

  from __future__ import annotations

  # ruff: noqa: F401
  import pandas as pd
  import requests
  from defusedxml import (
      ElementTree as ETree,  # nosec B405 - defusedxml hardens XML parsing
  )

  from eurlex.celex import get_celex_id, get_possible_celex_ids
  from eurlex.constants import ISO2_TO_ISO3, ISO3_TO_ISO2, PREFIXES
  from eurlex.fetch import (
      DEFAULT_REQUEST_TIMEOUT,
      _build_multichoice_item,
      _build_request_headers,
      _get_html,
      _parse_multichoice_html,
      _parse_optional_int,
      _select_multichoice_url,
      get_html_by_celex_id,
      get_html_by_cellar_id,
  )
  from eurlex.language import _normalize_language
  from eurlex.markup import get_tag_name
  from eurlex.parser import (
      _get_normalized_classes,
      _get_text,
      _has_normalized_class,
      _has_normalized_class_prefix,
      parse_article,
      parse_article_paragraphs,
      parse_html,
      parse_modifiers,
      parse_span,
      process_paragraphs,
  )
  from eurlex.uri import _add_query_param, get_prefixes, simplify_iri

  __all__ = [
      "pd",
      "requests",
      "ETree",
      "get_celex_id",
      "get_possible_celex_ids",
      "PREFIXES",
      "ISO2_TO_ISO3",
      "ISO3_TO_ISO2",
      "DEFAULT_REQUEST_TIMEOUT",
      "_build_multichoice_item",
      "_build_request_headers",
      "_get_html",
      "_parse_multichoice_html",
      "_parse_optional_int",
      "_select_multichoice_url",
      "get_html_by_cellar_id",
      "get_html_by_celex_id",
      "_normalize_language",
      "_get_normalized_classes",
      "_get_text",
      "_has_normalized_class",
      "_has_normalized_class_prefix",
      "parse_article",
      "parse_article_paragraphs",
      "parse_html",
      "parse_modifiers",
      "parse_span",
      "process_paragraphs",
      "_add_query_param",
      "get_prefixes",
      "simplify_iri",
      "get_tag_name",
  ]
  ```

- [ ] **Step 2: Verify both used functions still import cleanly**

  ```bash
  source .venv/bin/activate
  python -c "from eurlex import get_html_by_celex_id, parse_html; print('OK')"
  ```

  Expected output: `OK`

- [ ] **Step 3: Commit**

  ```bash
  git add vendor/eurlex/public.py
  git commit -m "refactor: remove unused SPARQL imports from vendor public facade"
  ```

---

## Task 3: Remove rdflib and SPARQLWrapper from requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Replace `requirements.txt`**

  ```
  fastapi
  uvicorn[standard]
  slowapi
  pandas~=3.0.1
  defusedxml~=0.7.1
  requests~=2.33.0
  lxml~=6.0.2
  ```

- [ ] **Step 2: Reinstall deps to verify nothing breaks**

  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python -c "from main import app; print('OK')"
  ```

  Expected: `OK` with no import errors. (rdflib and SPARQLWrapper may still be present in `.venv` from the previous install — that's fine, they just won't be installed on Railway.)

- [ ] **Step 3: Start the server and hit /health to verify runtime is fine**

  ```bash
  source .venv/bin/activate
  uvicorn main:app --port 8001 &
  sleep 2
  curl http://localhost:8001/health
  kill %1
  ```

  Expected: `{"status":"ok","cached_documents":0}`

- [ ] **Step 4: Commit**

  ```bash
  git add requirements.txt
  git commit -m "chore: remove unused rdflib and SPARQLWrapper dependencies"
  ```

---

## Task 4: Add Procfile for Railway

Railway uses a `Procfile` to know how to start your app. It injects a `$PORT` environment variable — your server must bind to that port or Railway won't route traffic to it.

**Files:**
- Create: `Procfile`

- [ ] **Step 1: Create `Procfile`**

  ```
  web: uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

- [ ] **Step 2: Verify it works locally with a custom PORT**

  ```bash
  source .venv/bin/activate
  PORT=9000 uvicorn main:app --host 0.0.0.0 --port 9000 &
  sleep 2
  curl http://localhost:9000/health
  kill %1
  ```

  Expected: `{"status":"ok","cached_documents":0}`

- [ ] **Step 3: Commit**

  ```bash
  git add Procfile
  git commit -m "feat: add Procfile for Railway deployment"
  ```

---

## Task 5: Update vercel.json and .vercelignore

Strip `vercel.json` to static-only. Expand `.vercelignore` so Vercel doesn't try to process any Python files.

**Files:**
- Modify: `vercel.json`
- Modify: `.vercelignore`

- [ ] **Step 1: Replace `vercel.json`**

  ```json
  { "outputDirectory": "public" }
  ```

- [ ] **Step 2: Replace `.vercelignore`**

  ```
  .venv/
  **/__pycache__/
  *.pyc
  main.py
  cache.py
  converter.py
  vendor/
  requirements.txt
  Procfile
  docs/
  TASKS.md
  ```

- [ ] **Step 3: Commit**

  ```bash
  git add vercel.json .vercelignore
  git commit -m "feat: configure Vercel for static-only frontend deploy"
  ```

---

## Task 6: Deploy to Railway and get your URL

Railway is a managed hosting platform — think Heroku. You push your repo, it detects Python via `requirements.txt`, installs deps, and runs your `Procfile`. No Docker or config files beyond what you've already added.

- [ ] **Step 1: Sign up at railway.app**

  Go to https://railway.app and sign in with GitHub.

- [ ] **Step 2: Create a new project**

  Click **New Project** → **Deploy from GitHub repo** → select this repo → **Deploy Now**.

  Railway will:
  1. Clone your repo
  2. Detect Python (via `requirements.txt`)
  3. Run `pip install -r requirements.txt`
  4. Start your app using the `Procfile`

- [ ] **Step 3: Watch the build logs**

  In the Railway dashboard, click your service → **Deployments** tab → open the latest deployment → check **Build Logs** and then **Deploy Logs**.

  A successful deploy ends with something like:
  ```
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:XXXX
  ```

- [ ] **Step 4: Get your Railway URL**

  In the Railway dashboard: click your service → **Settings** → **Networking** → **Generate Domain**.

  Railway assigns a URL like `https://yourapp-production.up.railway.app`.

  Copy this URL — you'll use it in the next task.

- [ ] **Step 5: Verify the backend is live**

  ```bash
  curl https://YOUR_RAILWAY_URL/health
  ```

  Expected: `{"status":"ok","cached_documents":0}`

---

## Task 7: Wire the Railway URL into the frontend

**Files:**
- Modify: `public/index.html` — line ~709 (`const API_BASE`)

- [ ] **Step 1: Find the current API_BASE line**

  It's near the top of the `<script>` block, around line 709:

  ```js
  const API_BASE = window.location.protocol === 'file:' ? 'http://localhost:8001' : '';
  ```

- [ ] **Step 2: Replace it with the Railway URL**

  Substitute your actual Railway URL for `YOUR_RAILWAY_URL`:

  ```js
  const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001'
    : 'https://YOUR_RAILWAY_URL';
  ```

  This keeps local development working (pointing at your local uvicorn) while production points at Railway.

- [ ] **Step 3: Verify locally that the constant looks right**

  Open `public/index.html` in a browser via `file://` — open the browser console and run:

  ```js
  console.log(API_BASE)
  ```

  Expected when opened as file://: `http://localhost:8001`

- [ ] **Step 4: Commit and push**

  ```bash
  git add public/index.html
  git commit -m "feat: point frontend API_BASE at Railway backend URL"
  git push
  ```

---

## Task 8: Verify the full deployment

- [ ] **Step 1: Check Vercel deployed the new frontend**

  Open your Vercel project URL. The page should load. Open the browser console — no errors about a missing backend.

- [ ] **Step 2: Convert a document end-to-end**

  On the live Vercel site, click the **EU AI Act** chip. Wait for the conversion (it hits the CELLAR API, which can take 5–15 seconds on first fetch).

  Expected: the right panel fills with rendered Markdown, the chat shows "Converted successfully."

- [ ] **Step 3: Verify the CORS header is present**

  ```bash
  curl -I -X GET https://YOUR_RAILWAY_URL/health \
    -H "Origin: https://YOUR_VERCEL_URL"
  ```

  Expected: response includes `access-control-allow-origin: *`

- [ ] **Step 4: Check Railway logs after the request**

  In Railway dashboard → your service → **Deployments** → **Deploy Logs**. You should see the GET request logged by uvicorn.

---

## Local development after this change

The local workflow is unchanged:

```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8001
```

Open `public/index.html` directly in your browser (file://) — `API_BASE` auto-selects `http://localhost:8001`.
