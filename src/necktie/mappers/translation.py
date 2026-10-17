"""Helpers for picking localized translations."""

import langcodes


def pick_translation(translations: list, language: str):
    """Return the translation for ``language``, falling back to the first.

    Uses standard BCP 47 matching via ``langcodes.closest_match``, so variants
    like ``zh-Hant-HK`` resolve to the closest available translation.
    """
    if not translations:
        return None
    for t in translations:
        if t.language_code == language:
            return t
    available = [t.language_code for t in translations]
    match, _distance = langcodes.closest_match(language, available)
    if match == "und":
        return translations[0]
    return next(t for t in translations if t.language_code == match)
