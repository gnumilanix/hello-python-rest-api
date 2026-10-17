"""Shared cross-cutting constants."""

# Max length of a BCP 47 language tag (RFC 5646 §4.4.1 recommends >= 35).
LANGUAGE_CODE_LENGTH = 35

# Application is Hong Kong-only; phone numbers are validated against this region.
DEFAULT_PHONE_REGION = "HK"
