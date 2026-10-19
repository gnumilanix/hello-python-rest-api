"""Shared translatable-text schemas (en/yue/zh)."""

from pydantic import BaseModel, Field

# Matches the VARCHAR(255) columns in the database.
_MAX_TEXT = 255


class LocaleModel(BaseModel):
    """Text present in every supported language (non-empty)."""

    en: str = Field(min_length=1, max_length=_MAX_TEXT)
    yue: str = Field(min_length=1, max_length=_MAX_TEXT)
    zh: str = Field(min_length=1, max_length=_MAX_TEXT)


class NullableLocaleModel(BaseModel):
    """Translatable text where any language may be absent (non-empty if present)."""

    en: str | None = Field(default=None, min_length=1, max_length=_MAX_TEXT)
    yue: str | None = Field(default=None, min_length=1, max_length=_MAX_TEXT)
    zh: str | None = Field(default=None, min_length=1, max_length=_MAX_TEXT)
