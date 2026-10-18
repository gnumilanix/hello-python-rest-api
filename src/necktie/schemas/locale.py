"""Shared translatable-text schemas (en/yue/zh)."""

from pydantic import BaseModel


class LocaleModel(BaseModel):
    """Text present in every supported language."""

    en: str
    yue: str
    zh: str


class NullableLocaleModel(BaseModel):
    """Translatable text where any language may be absent."""

    en: str | None = None
    yue: str | None = None
    zh: str | None = None
