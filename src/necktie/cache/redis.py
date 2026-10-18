"""Redis client factory."""

import os
from pathlib import Path

from dotenv import load_dotenv
from redis import asyncio as aioredis

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

REDIS_URL = os.getenv("REDIS_URL") or (
    f"redis://localhost:{os.environ.get('REDIS_PORT', '6379')}/0"
)


def create_redis_client() -> aioredis.Redis:
    """Build the Redis client used by the app."""
    return aioredis.from_url(REDIS_URL)
