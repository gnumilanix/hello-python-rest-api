# necktie

A Python package, to be served as an API and packaged with Docker.

## Domain assumptions

Hong Kong–specific rules that shape the data model and API:

- **Hong Kong only.** Phone numbers are validated against the HK region, and only on create — reads return whatever is stored.
- **One row per clinic.** A doctor with multiple clinics is stored as one
  row per clinic (name clashes make deduplication unreliable), so there is no
  separate clinic table.
- **Public holidays are all-or-nothing.** HK clinics either open or close on
  public holidays as a whole, regardless of which weekday a holiday falls on —
  so `is_open_on_public_holidays` is a single flag, not per-day.
- **`place_id` is the Google Places ID** for a clinic, used for navigation.
- **Day of week follows ISO 8601** (1 = Monday, 7 = Sunday) in `operating_hours`.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

## Lint

```bash
ruff check .
ruff format --check .
```

## Project structure

```
├── pyproject.toml      # Package metadata and tool config
├── src/
│   └── necktie/         # Package source
│       ├── __init__.py
│       └── main.py
└── tests/              # Test suite
```
