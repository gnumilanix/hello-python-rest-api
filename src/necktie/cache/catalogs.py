"""Redis-backed store for lazily loaded reference-data catalogs."""

from collections.abc import Callable, Coroutine, Iterable
from typing import Generic, TypeVar

from fastapi_cache import FastAPICache
from pydantic import TypeAdapter

from necktie.cache.lifespan import CACHE_TTL_SECONDS

EntryT = TypeVar("EntryT")


class CatalogStore(Generic[EntryT]):
    """Caches a serialized catalog in Redis, populating it on first request."""

    def __init__(
        self,
        key: str,
        adapter: TypeAdapter[list[EntryT]],
        load: Callable[[], Coroutine[object, object, Iterable[EntryT]]],
    ) -> None:
        self.key = key
        self.adapter = adapter
        self.load = load

    async def get(self) -> list[EntryT]:
        """Return the catalog from Redis, loading and caching it on a miss."""
        backend = FastAPICache.get_backend()
        cached = await backend.get(self.key)
        if cached is not None:
            return self.adapter.validate_json(cached)
        entries = list(await self.load())
        await backend.set(
            self.key,
            self.adapter.dump_json(entries),
            expire=CACHE_TTL_SECONDS,
        )
        return entries
