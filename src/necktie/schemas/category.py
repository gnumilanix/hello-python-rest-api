"""Localized category response schema."""

from pydantic import BaseModel


class Category(BaseModel):
    """Category with a single localized name."""

    id: int
    name_key: str
    name: str
