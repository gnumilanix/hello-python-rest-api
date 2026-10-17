"""Localized category reference."""

from pydantic import BaseModel


class CategoryRef(BaseModel):
    """Category reference with a single localized name."""

    id: int
    name: str
