"""Redis-backed caching for read results.

Aspect-oriented: read methods are decorated with ``@cached(resource)`` and
mutations with ``@flushes_cache`` — no manual key handling at call sites.
Keys derive from the resource name + bound arguments; cached JSON is decoded
back into the method's annotated return type.
"""

import functools
import inspect
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, ParamSpec, TypeVar, get_args, get_origin, get_type_hints

import redis
from dotenv import load_dotenv
from pydantic import BaseModel

P = ParamSpec("P")
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


def cached(resource: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Cache the decorated read method under ``resource`` + bound arguments."""

    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        signature = inspect.signature(fn)
        decode: Callable[[Any], T] | None = None

        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            nonlocal decode
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            params = {
                name: value
                for name, value in bound.arguments.items()
                if name != "self"
            }
            key = build_key(resource, params)
            hit = get(key)
            if hit is not None:
                if decode is None:
                    decode = _resolve_decoder(fn)
                return decode(hit)
            result = fn(*args, **kwargs)
            if isinstance(result, list):
                set(key, [_dump(item) for item in result])
            else:
                set(key, _dump(result))
            return result

        return wrapper

    return decorator


def flushes_cache(fn: Callable[P, T]) -> Callable[P, T]:
    """Flush every cached key after the decorated mutation completes."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        result = fn(*args, **kwargs)
        invalidate_all()
        return result

    return wrapper


def _resolve_decoder(fn: Callable[..., T]) -> Callable[[Any], T]:
    """Build a JSON→model decoder from ``fn``'s return annotation."""
    hint = get_type_hints(fn).get("return")
    if get_origin(hint) is list:
        (model,) = get_args(hint)
        if isinstance(model, type) and issubclass(model, BaseModel):
            return lambda data: [model.model_validate(item) for item in data]
    if isinstance(hint, type) and issubclass(hint, BaseModel):
        return hint.model_validate
    return lambda data: data


def _dump(value: object) -> object:
    """Serialize a Pydantic model (or pass through) to JSON-safe data."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value

