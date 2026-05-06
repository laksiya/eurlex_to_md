import os

from fastapi import HTTPException, Request

_UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
_UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
_LIMIT = 10
_WINDOW = 60  # seconds

if _UPSTASH_URL and _UPSTASH_TOKEN:
    from upstash_redis import Redis
    _redis = Redis(url=_UPSTASH_URL, token=_UPSTASH_TOKEN)
else:
    _redis = None


def _get_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limit(request: Request) -> None:
    if _redis is None:
        return  # no-op: in-memory fallback for local dev has no distributed state

    ip = _get_ip(request)
    key = f"ratelimit:{ip}"

    # Pipeline keeps INCR + EXPIRE atomic from the client's perspective
    pipe = _redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, _WINDOW)
    count, _ = pipe.execute()

    if count > _LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {_LIMIT} requests per {_WINDOW}s",
        )
