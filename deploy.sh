#!/usr/bin/env bash
set -euo pipefail

IMAGE=${1:-}
PROJECT=${2:-}
REGION=${3:-us-central1}
SERVICE=${4:-tomato-app}

if [ -z "$IMAGE" ]; then
  echo "Usage: ./deploy.sh <image> <gcp-project> [region] [service]"
  exit 1
fi

if [ -z "$PROJECT" ]; then
  echo "Missing GCP project. Usage: ./deploy.sh <image> <gcp-project> [region] [service]"
  exit 1
fi

echo "Deploying $IMAGE to Cloud Run service $SERVICE in project $PROJECT (region $REGION)"

# Authenticate must be done prior to running this script (gcloud auth login or service account)
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --project "$PROJECT" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --concurrency 1
