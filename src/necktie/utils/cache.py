"""Redis-backed caching for read results.

Reads are cached by a key derived from resource name + filter params.
Mutations flush the whole cache so stale reads are never served.
"""

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar, cast

import redis
from dotenv import load_dotenv

T = TypeVar("T")

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

REDIS_URL = os.getenv("REDIS_URL") or (
    f"redis://localhost:{os.environ.get('REDIS_PORT', '6379')}/0"
)

CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "300"))

_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

KEY_PREFIX = "necktie:"


def build_key(resource: str, params: dict) -> str:
    """Build a cache key from the resource name and filter params."""
    items = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)
    return f"{KEY_PREFIX}{resource}?{items}"


def get(key: str) -> dict | list | None:
    """Return the cached response for ``key``, or None."""
    raw = _client.get(key)
    return json.loads(raw) if raw is not None else None


def set(key: str, value: object) -> None:
    """Cache ``value`` under ``key`` with the configured TTL."""
    _client.set(key, json.dumps(value), ex=CACHE_TTL_SECONDS)


def invalidate_all() -> None:
    """Flush every cached key (called on any mutation)."""
    for key in _client.scan_iter(f"{KEY_PREFIX}*"):
        _client.delete(key)


def get_or_fetch(
    key: str,
    fetch: Callable[[], T],
    decode: Callable[[Any], T] | None = None,
) -> T:
    """Return the cached value for ``key``, else call ``fetch``, cache, return it.

    On a hit, ``decode`` (if given) converts the raw JSON back into ``T``.
    ``fetch`` returns Pydantic models (or dicts); results are stored via their
    ``model_dump()``/JSON-able form and served back on subsequent hits.
    """
    hit = get(key)
    if hit is not None:
        return decode(hit) if decode is not None else cast(T, hit)
    result = fetch()
    if isinstance(result, list):
        set(key, [_dump(r) for r in result])
    else:
        set(key, _dump(result))
    return result


def _dump(value: object) -> object:
    """Serialize a Pydantic model (or pass through) to JSON-safe data."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value

