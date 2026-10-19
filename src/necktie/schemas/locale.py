"""Shared translatable-text schemas (en/yue/zh)."""

from pydantic import BaseModel, Field


class LocaleModel(BaseModel):
    """Text present in every supported language (non-empty)."""

    en: str = Field(min_length=1)
    yue: str = Field(min_length=1)
    zh: str = Field(min_length=1)


class NullableLocaleModel(BaseModel):
    """Translatable text where any language may be absent (non-empty if present)."""

    en: str | None = Field(default=None, min_length=1)
    yue: str | None = Field(default=None, min_length=1)
    zh: str | None = Field(default=None, min_length=1)
