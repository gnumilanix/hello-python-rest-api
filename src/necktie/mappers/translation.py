"""Helpers for picking localized translations."""


def pick_translation(translations: list, language: str):
    """Return the translation for ``language``, falling back to the first."""
    for t in translations:
        if t.language_code == language:
            return t
    return translations[0] if translations else None
