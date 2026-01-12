#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/build_and_run.sh [image-name] [model-url]
# Example: ./scripts/build_and_run.sh tomato-app:latest https://example.com/tomato_model.h5

IMAGE_NAME="${1:-tomato-app:latest}"
MODEL_URL="${2:-}"

echo "Building image ${IMAGE_NAME}..."
docker build -t "${IMAGE_NAME}" .

RUN_ARGS=(--rm -p 5000:5000 -e PORT=5000 -v "$(pwd)/static/uploads":/app/static/uploads)

if [ -n "${MODEL_URL}" ]; then
  RUN_ARGS+=( -e MODEL_URL="${MODEL_URL}" )
fi

echo "Running container from ${IMAGE_NAME}..."
docker run "${RUN_ARGS[@]}" "${IMAGE_NAME}"
