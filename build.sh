#!/usr/bin/env bash
set -e

echo "=== STEP 1: Upgrading pip ==="
pip install --upgrade pip

echo "=== STEP 2: Installing dependencies ==="
pip install -r requirements.txt

echo "=== STEP 3: Downloading ONNX model ==="
mkdir -p models

FILE_ID="1tr7cbowX-OdEFIpG3d4c0bcYeZfdSHgI"
OUTPUT="models/tomato_model.onnx"

# Try gdown first
echo "Trying gdown..."
python -c "
import gdown, os
gdown.download(
    'https://drive.google.com/uc?id=1tr7cbowX-OdEFIpG3d4c0bcYeZfdSHgI',
    'models/tomato_model.onnx',
    quiet=False,
    fuzzy=True
)
"

# Check if gdown worked
if [ -f "$OUTPUT" ] && [ $(wc -c < "$OUTPUT") -gt 1048576 ]; then
    echo "=== gdown SUCCESS: $(du -sh $OUTPUT) ==="
else
    echo "gdown failed — trying wget..."
    rm -f "$OUTPUT"

    # Try wget with Google Drive export URL
    wget --no-check-certificate \
         "https://docs.google.com/uc?export=download&id=${FILE_ID}" \
         -O "$OUTPUT" \
         --quiet --show-progress

    # Check if wget worked
    if [ -f "$OUTPUT" ] && [ $(wc -c < "$OUTPUT") -gt 1048576 ]; then
        echo "=== wget SUCCESS: $(du -sh $OUTPUT) ==="
    else
        echo "wget failed — trying curl..."
        rm -f "$OUTPUT"

        # Try curl
        curl -L \
             "https://drive.google.com/uc?export=download&id=${FILE_ID}&confirm=t" \
             -o "$OUTPUT"

        if [ -f "$OUTPUT" ] && [ $(wc -c < "$OUTPUT") -gt 1048576 ]; then
            echo "=== curl SUCCESS: $(du -sh $OUTPUT) ==="
        else
            echo "=== ALL DOWNLOAD METHODS FAILED ==="
            rm -f "$OUTPUT"
            exit 1
        fi
    fi
fi

echo "=== BUILD COMPLETE ==="
echo "Model file: $(ls -lh $OUTPUT)"
