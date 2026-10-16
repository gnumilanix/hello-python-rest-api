"""Database engine and session management."""

import os
from collections.abc import Iterator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"postgresql+psycopg://{os.environ['POSTGRES_USER']}"
    f":{os.environ['POSTGRES_PASSWORD']}"
    f"@localhost:{os.environ.get('POSTGRES_PORT', '5432')}"
    f"/{os.environ['POSTGRES_DB']}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
