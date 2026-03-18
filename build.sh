#!/usr/bin/env bash
set -e
#!/usr/bin/env bash
set -e

echo "=== STEP 1: Upgrading pip ==="
pip install --upgrade pip

echo "=== STEP 2: Installing dependencies ==="
#!/usr/bin/env bash
set -e
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "Build complete."
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
