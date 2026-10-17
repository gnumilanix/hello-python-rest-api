"""Localized district response schema."""

from pydantic import BaseModel


class District(BaseModel):
    """District with a single localized name."""

    id: int
    sort_order: int
    name: str
