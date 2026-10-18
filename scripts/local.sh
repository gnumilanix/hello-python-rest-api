#!/usr/bin/env bash
# Run the full stack locally in Docker: infra + app (builds the image).
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.local.yml"

echo "Building and starting the full stack..."
$COMPOSE up --build -d

echo "Waiting for the app..."
until curl -sf http://localhost:"${APP_PORT:-8000}"/health >/dev/null 2>&1; do sleep 1; done

echo "App is running at http://localhost:${APP_PORT:-8000}"
echo "Docs at http://localhost:${APP_PORT:-8000}/docs"
