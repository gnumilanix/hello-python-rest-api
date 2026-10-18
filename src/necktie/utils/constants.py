"""Shared cross-cutting constants."""

# Max length of a BCP 47 language tag (RFC 5646 §4.4.1 recommends >= 35).
LANGUAGE_CODE_LENGTH = 35

# Fallback language when a requested translation is missing.
DEFAULT_LANGUAGE = "en-US"

# Phone region for validation (see README "Domain assumptions").
DEFAULT_PHONE_REGION = "HK"
