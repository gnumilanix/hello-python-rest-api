# bowtie

A Python package, to be served as an API and packaged with Docker.

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
│   └── bowtie/         # Package source
│       ├── __init__.py
│       └── main.py
└── tests/              # Test suite
```
