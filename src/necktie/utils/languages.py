"""Supported languages (Hong Kong product: English, Cantonese, Mandarin)."""

from enum import StrEnum

from necktie.utils.constants import DEFAULT_LANGUAGE


class Language(StrEnum):
    """Languages the API serves; ``.default()`` gives the fallback."""

    EN = "en"  # English
    YUE = "yue"  # Cantonese
    ZH = "zh"  # Mandarin

    @classmethod
    def default(cls) -> "Language":
        """The fallback language."""
        return cls(DEFAULT_LANGUAGE)
