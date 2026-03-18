#!/usr/bin/env bash
set -e

echo "======================================"
echo " STARTUP: Downloading model"
echo "======================================"

mkdir -p models

MODEL_PATH="models/tomato_model.onnx"
MODEL_URL="https://huggingface.co/karthik049/tomato-disease-model/resolve/main/tomato_model.onnx"

if [ ! -f "$MODEL_PATH" ] || [ $(wc -c < "$MODEL_PATH") -lt 1048576 ]; then
  echo "Downloading from HuggingFace..."
  wget \
    --progress=dot:mega \
    --tries=3 \
    --timeout=300 \
    --no-check-certificate \
    -O "$MODEL_PATH" \
    "$MODEL_URL"
  echo "Download complete: $(du -sh $MODEL_PATH)"
else
  echo "Model already exists: $(du -sh $MODEL_PATH)"
fi

echo "======================================"
echo " Starting gunicorn..."
echo "======================================"

exec gunicorn app:app \
  --workers 1 \
  --timeout 120 \
  --bind 0.0.0.0:$PORT
