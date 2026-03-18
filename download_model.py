"""
Auto-download ONNX model from Google Drive if not present.
This runs on app startup in production.
"""
"""
Auto-download ONNX model from Google Drive if not present.
This runs on app startup in production.
"""
import os
import gdown

MODEL_PATH      = os.getenv('MODEL_PATH', 'models/tomato_model.onnx')
FILE_ID         = os.getenv('GOOGLE_DRIVE_MODEL_ID', '1tr7cbowX-OdEFIpG3d4c0bcYeZfdSHgI')
DRIVE_URL       = f"https://drive.google.com/uc?id={FILE_ID}&export=download"
DRIVE_FUZZY_URL = f"https://drive.google.com/file/d/{FILE_ID}/view"

def _valid(path):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    if size < 1024 * 1024:  # less than 1MB = definitely wrong
        return False
    # Check file starts with ONNX magic bytes (not HTML)
    with open(path, 'rb') as f:
        header = f.read(8)
    # ONNX files start with protobuf bytes (0x08), not HTML (<)
    if header[0:1] == b'<':
        print("Downloaded file is HTML not ONNX!")
        print("Google Drive returned a warning page.")
        print("Fix: re-share file as 'Anyone with the link'")
        return False
    return True

def ensure_model():
    """Download model from Google Drive if not already present."""
    if _valid(MODEL_PATH):
        print(f"✓ Model valid: {os.path.getsize(MODEL_PATH)/1024/1024:.1f} MB")
        return True
    else:
        print("Model file invalid — removing and re-downloading")
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)

    if not FILE_ID:
        print("⚠ GOOGLE_DRIVE_MODEL_ID not set. Model auto-download disabled.")
        print("  Set this env var to enable automatic model downloads.")
        return False

    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        print(f"📥 Downloading ONNX model from Google Drive...")

        url = DRIVE_URL
        gdown.download(url, MODEL_PATH, quiet=False)

        if _valid(MODEL_PATH):
            print(f"✓ Model downloaded successfully: {MODEL_PATH}")
            return True
        else:
            print("✗ Model download failed: file is invalid after download.")
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
            return False
    except Exception as e:
        print(f"✗ Model download failed: {e}")
        return False

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    ensure_model()
