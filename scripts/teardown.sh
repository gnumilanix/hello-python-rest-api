#!/usr/bin/env bash
# Tear down the full local environment: containers, volumes, port, venv, caches.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Stopping containers and removing volumes..."
docker compose -f docker-compose.yml -f docker-compose.local.yml down -v

echo "Freeing port ${APP_PORT:-8000}..."
lsof -ti :"${APP_PORT:-8000}" | xargs kill -9 2>/dev/null || true

echo "Removing venv and caches..."
rm -rf .venv
find . -type d \( \
    -name __pycache__ -o \
    -name .pytest_cache -o \
    -name .ruff_cache -o \
    -name .mypy_cache \
\) -exec rm -rf {} + 2>/dev/null || true
rm -f .coverage coverage.xml

echo "Teardown complete. .env and source are untouched."
