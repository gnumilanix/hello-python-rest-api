"""District reference with all translations."""

from pydantic import BaseModel


class DistrictTranslated(BaseModel):
    """District reference with all translations."""

    id: int
    name: dict[str, str]
