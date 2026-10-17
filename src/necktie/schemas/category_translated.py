"""Category reference with all translations."""

from pydantic import BaseModel


class CategoryTranslated(BaseModel):
    """Category reference with all translations."""

    id: int
    name: dict[str, str]
