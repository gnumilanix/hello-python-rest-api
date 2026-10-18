#!/usr/bin/env bash
# Verify the codebase: lint, type-check, security scan, tests, Docker build.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Lint ==="
.venv/bin/ruff check src/ tests/

echo "=== Type check ==="
.venv/bin/mypy src/

echo "=== Security scan ==="
.venv/bin/bandit -r src/ --exclude src/.venv

echo "=== Tests ==="
docker compose up -d postgres redis
until docker compose exec -T postgres pg_isready -q 2>/dev/null; do sleep 1; done
(cd jetbase && ../.venv/bin/jetbase upgrade)
.venv/bin/pytest -q

echo "=== Docker build ==="
scripts/build.sh

echo "All checks passed."
