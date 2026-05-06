import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "vendor"))

import requests as _requests
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from cache import cache
from converter import dataframe_to_markdown
from ratelimit import rate_limit
from eurlex import get_html_by_celex_id, parse_html

app = FastAPI(title="eurlex-to-md", description="Convert EUR-Lex CELEX IDs to Markdown")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "OPTIONS"], allow_headers=["*"])


@app.get("/generate/{celex_id}")
async def generate(celex_id: str, request: Request, _: None = Depends(rate_limit)):
    cached = cache.get(celex_id)
    if cached:
        return JSONResponse(content=cached)

    try:
        html = get_html_by_celex_id(celex_id)
    except (_requests.exceptions.ConnectionError, _requests.exceptions.Timeout) as e:
        raise HTTPException(status_code=503, detail="CELLAR API unreachable") from e

    if not html or len(html.strip()) < 100:
        raise HTTPException(status_code=404, detail=f"No document found for CELEX ID: {celex_id}")

    df = parse_html(html)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Document found but could not be parsed: {celex_id}")

    markdown, title, article_count = dataframe_to_markdown(df)

    result = {
        "celex_id": celex_id.upper(),
        "title": title,
        "article_count": article_count,
        "markdown": markdown,
    }
    cache.set(celex_id, result)
    return JSONResponse(content=result)


@app.get("/health")
async def health():
    return {"status": "ok", "cached_documents": cache.size()}
