"""Localized district reference."""

from pydantic import BaseModel


class DistrictRef(BaseModel):
    """District reference with a single localized name."""

    id: int
    name: str
