"""
Auto-download ONNX model from Google Drive if not present.
This runs on app startup in production.
"""
import os
import gdown

MODEL_PATH = os.getenv('MODEL_PATH', 'models/tomato_model.onnx')
MODEL_ID = os.getenv('GOOGLE_DRIVE_MODEL_ID', '')

def ensure_model():
    """Download model from Google Drive if not already present."""
    if os.path.exists(MODEL_PATH):
        print(f"✓ Model already exists at {MODEL_PATH}")
        return True
    
    if not MODEL_ID:
        print("⚠ GOOGLE_DRIVE_MODEL_ID not set. Model auto-download disabled.")
        print("  Set this env var to enable automatic model downloads.")
        return False
    
    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        print(f"📥 Downloading ONNX model from Google Drive...")
        
        url = f"https://drive.google.com/uc?id={MODEL_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)
        
        print(f"✓ Model downloaded successfully: {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"✗ Model download failed: {e}")
        return False

if __name__ == '__main__':
    ensure_model()
