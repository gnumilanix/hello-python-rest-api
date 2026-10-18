"""Shared cross-cutting constants."""

# Max length of a BCP 47 language tag (RFC 5646 §4.4.1 recommends >= 35).
LANGUAGE_CODE_LENGTH = 35

# Fallback language when a requested translation is missing.
DEFAULT_LANGUAGE = "en-US"

# Application is Hong Kong-only; phone numbers are validated against this region.
DEFAULT_PHONE_REGION = "HK"
