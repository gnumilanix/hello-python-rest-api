"""HTTP response cache (fastapi-cache2 backed by Redis)."""

import os
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.requests import Request
from starlette.responses import Response

from necktie.cache.redis import create_redis_client

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "300"))


def request_key_builder(
    _: Callable,
    namespace: str = "",
    *,
    request: Request | None = None,
    response: Response | None = None,
    **_kwargs: object,
) -> str:
    """Key from request path + sorted query params (ignores injected deps)."""
    if request is None:
        raise ValueError("request is required for cache key building")
    items = "&".join(f"{k}={v}" for k, v in sorted(request.query_params.items()))
    return f"{namespace}:{request.url.path}?{items}"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Init fastapi-cache2 against Redis for the app lifetime."""
    redis = create_redis_client()
    FastAPICache.init(
        RedisBackend(redis),
        prefix="necktie",
        expire=CACHE_TTL_SECONDS,
        key_builder=request_key_builder,
    )
    yield
