"""
Google Drive Model Download Module (Option B)

This module provides a function to download the tomato disease model from Google Drive
at application startup if the local model file is missing.

Usage:
    from model_downloader import ensure_model_exists
    ensure_model_exists()
    model = tf.keras.models.load_model('models/tomato_model.h5')

Environment Variables:
    MODEL_URL: Google Drive file ID or full shareable link (required)
    MODEL_PATH: Path to save the model (default: models/tomato_model.h5)

Setup:
    1. Upload tomato_model.h5 to Google Drive
    2. Right-click file → Share → Change to "Anyone with link can view"
    3. Copy the file ID from the shareable link (the part between /d/ and /view)
    4. Set environment variable: MODEL_URL=your_file_id
    5. Install gdown: pip install gdown
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
    model_path: str = "models/tomato_model.h5",
    model_url: Optional[str] = None
) -> bool:
    """
    Ensure the model file exists, downloading from Google Drive if necessary.

    Args:
        model_path: Path where the model should be located (default: models/tomato_model.h5)
        model_url: Google Drive file ID or env var name (if None, reads MODEL_URL from env)

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
        model_url = os.getenv("MODEL_URL", "").strip()

    if not model_url:
        logger.warning(
            f"Model not found at {model_path} and MODEL_URL not set. "
            "Unable to download model. "
            "Set MODEL_URL environment variable with Google Drive file ID."
        )
        print(f"⚠️ Warning: Model not found and MODEL_URL not configured")
        return False

    # Download model from Google Drive
    logger.info(f"Model not found. Attempting download from Google Drive...")
    print(f"📥 Model not found. Downloading from Google Drive...")
    
    success = download_from_google_drive(
        file_id=model_url,
        output_path=model_path,
        quiet=False
    )

    return success


def get_model_url_from_drive_link(shareable_link: str) -> str:
    """
    Extract Google Drive file ID from a shareable link.

    Args:
        shareable_link: Full Google Drive shareable link
        (e.g., https://drive.google.com/file/d/FILE_ID/view?usp=sharing)

    Returns:
        File ID suitable for use with gdown
    """
    if "/d/" in shareable_link:
        file_id = shareable_link.split("/d/")[1].split("/")[0]
        return file_id
    return shareable_link


if __name__ == "__main__":
    # Example usage
    print("🧪 Testing model downloader...")
    
    # Check if gdown is available
    if gdown is None:
        print("❌ gdown not installed. Install with: pip install gdown")
        sys.exit(1)
    
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
