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

def ensure_model():
    """Download model from Google Drive if not already present."""
    if os.path.exists(MODEL_PATH):
        print(f"✓ Model already exists at {MODEL_PATH}")
        return True
    
    if not FILE_ID:
        print("⚠ GOOGLE_DRIVE_MODEL_ID not set. Model auto-download disabled.")
        print("  Set this env var to enable automatic model downloads.")
        return False
    
    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        print(f"📥 Downloading ONNX model from Google Drive...")
        
        url = DRIVE_URL
        gdown.download(url, MODEL_PATH, quiet=False)
        
        print(f"✓ Model downloaded successfully: {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"✗ Model download failed: {e}")
        return False

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    ensure_model()
