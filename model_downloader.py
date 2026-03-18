
"""
HuggingFace Model Download Module

This module provides a function to download the tomato disease ONNX model from HuggingFace
at application startup if the local model file is missing.

Usage:
    from model_downloader import ensure_model_exists
    ensure_model_exists()

Environment Variables:
    MODEL_URL: HuggingFace ONNX file URL (default provided)
    MODEL_PATH: Path to save the model (default: models/tomato_model.onnx)
"""

import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import gdown; provide helpful error if not installed
try:
    import gdown
except ImportError:
    gdown = None


def download_from_google_drive(
    file_id: str,
    output_path: str,
    quiet: bool = False
) -> bool:
    """
    Download a file from Google Drive.

    Args:
        file_id: Google Drive file ID (the part between /d/ and /view in shareable link)
        output_path: Path where to save the downloaded file
        quiet: If True, suppress download progress output

    Returns:
        True if download successful, False otherwise

    Raises:
        ImportError: If gdown is not installed
    """
    if gdown is None:
        raise ImportError(
            "gdown is required for downloading from Google Drive. "
            "Install it with: pip install gdown"
        )

    try:
        # Construct Google Drive download URL
        url = f"https://drive.google.com/uc?id={file_id}"
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created directory: {output_dir}")

        logger.info(f"Downloading model from Google Drive: {file_id}")
        print(f"📥 Downloading model ({os.path.basename(output_path)})...")
        
        # Download the file
        gdown.download(url, output_path, quiet=quiet)
        
        # Verify file exists and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"✅ Model downloaded successfully ({size_mb:.2f} MB)")
            print(f"✅ Model downloaded successfully ({size_mb:.2f} MB)")
            return True
        else:
            logger.error("Downloaded file is empty or doesn't exist")
            return False

    except Exception as e:
        logger.error(f"Failed to download model from Google Drive: {e}")
        print(f"❌ Error downloading model: {e}")
        return False


def ensure_model_exists(
    model_path: str = "models/tomato_model.onnx",
    model_url: Optional[str] = None
) -> bool:
    """
    Ensure the ONNX model file exists, downloading from HuggingFace if necessary.

    Args:
        model_path: Path where the model should be located (default: models/tomato_model.onnx)
        model_url: HuggingFace ONNX file URL (if None, uses default)

    Returns:
        True if model exists (or was successfully downloaded), False otherwise
    """
    # If model already exists, nothing to do
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        logger.info(f"Model found at {model_path} ({size_mb:.2f} MB)")
        print(f"✅ Model found: {model_path}")
        return True

    # Get model URL from parameter or environment variable
    if model_url is None:
        model_url = os.getenv("MODEL_URL", "https://huggingface.co/karthik049/tomato-disease-model/resolve/main/tomato_model.onnx").strip()

    if not model_url:
        logger.warning(
            f"Model not found at {model_path} and MODEL_URL not set. "
            "Unable to download model. "
            "Set MODEL_URL environment variable with HuggingFace ONNX URL."
        )
        print(f"⚠️ Warning: Model not found and MODEL_URL not configured")
        return False

    # Download model from HuggingFace
    logger.info(f"Model not found. Attempting download from HuggingFace...")
    print(f"📥 Model not found. Downloading from HuggingFace...")
    
    import requests
    try:
        response = requests.get(model_url, stream=True, timeout=300)
        response.raise_for_status()
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        logger.info(f"✅ Model downloaded successfully ({size_mb:.2f} MB)")
        print(f"✅ Model downloaded successfully ({size_mb:.2f} MB)")
        return True
    except Exception as e:
        logger.error(f"Failed to download model from HuggingFace: {e}")
        print(f"❌ Error downloading model: {e}")
        return False



    # No longer needed: Google Drive logic removed
    return None



if __name__ == "__main__":
    print("🧪 Testing HuggingFace model downloader...")
    ensure_model_exists()
    
    # Example: Download using environment variable
    model_path = "models/tomato_model.h5"
    success = ensure_model_exists(model_path)
    
    if success:
        print("✅ Model is ready to use")
        sys.exit(0)
    else:
        print("❌ Model download failed or MODEL_URL not set")
        print("📌 To use Google Drive download, set: MODEL_URL=<your_file_id>")
        sys.exit(1)
