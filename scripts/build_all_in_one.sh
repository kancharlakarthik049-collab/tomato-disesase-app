#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/build_all_in_one.sh [image-name] [model-url]
# Example: ./scripts/build_all_in_one.sh tomato-app:allinone https://example.com/tomato_model.h5

IMAGE_NAME="${1:-tomato-app:allinone}"
MODEL_URL="${2:-}"

BUILD_ARGS=()
if [ -n "${MODEL_URL}" ]; then
  BUILD_ARGS+=(--build-arg "MODEL_URL=${MODEL_URL}")
fi

echo "Building all-in-one image ${IMAGE_NAME} using Dockerfile.allinone..."
docker build -f Dockerfile.allinone -t "${IMAGE_NAME}" "${BUILD_ARGS[@]:-}" .

echo "To run the image locally (port 5000):"
echo "  docker run --rm -p 5000:5000 ${IMAGE_NAME}"
