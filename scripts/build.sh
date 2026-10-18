#!/usr/bin/env bash
# Build the Docker image locally.
set -euo pipefail

IMAGE="${1:-necktie:local}"
echo "Building $IMAGE..."
docker build -t "$IMAGE" .
echo "Built $IMAGE"
