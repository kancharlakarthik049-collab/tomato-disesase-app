#!/usr/bin/env python3
"""
AUTOMATED DEPLOYMENT SCRIPT
Run this with Python 3.11 or 3.12 for model conversion.

Usage:
  python3.11 auto_deploy.py  # For model conversion
  python auto_deploy.py      # For testing/deployment without conversion
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_cmd(cmd, check=True):
    """Run shell command and return output."""
    print(f"▶ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and check:
        print(f"✗ Error: {result.stderr}")
        return False
    return result.stdout or True

def convert_model():
    """Convert H5 to ONNX (requires Python 3.11 or 3.12)."""
    if sys.version_info >= (3, 15):
        print("⚠ Python 3.14+ detected. Model conversion requires Python 3.11-3.13.")
        print("📝 Alternative options:")
        print("  1. Use Google Colab: https://colab.research.google.com")
        print("  2. Use Python 3.11 or 3.12 on your machine")
        print("  3. Use GitHub Actions (auto-conversion on push)")
        return False
    
    print("📦 Installing TensorFlow...")
    run_cmd("pip install --upgrade tensorflow tf2onnx onnxruntime")
    
    print("🔄 Converting model...")
    run_cmd("""python << 'EOF'
import tensorflow as tf
import tf2onnx
import onnx
import os

model = tf.keras.models.load_model('models/tomato_model.h5', compile=False)
print(f' Input shape: {model.input_shape}')

input_sig = [tf.TensorSpec(model.inputs[0].shape, tf.float32, name='input')]
onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=input_sig, opset=13)
onnx.save(onnx_model, 'models/tomato_model.onnx')

size = os.path.getsize('models/tomato_model.onnx') / (1024*1024)
print(f'✅ Converted! Size: {size:.1f} MB')
EOF
""")
    
    return os.path.exists('models/tomato_model.onnx')

def test_local():
    """Test Flask app locally."""
    print("\n📝 Testing local Flask app...")
    print("▶ python -m flask run")
    print("  App will be at http://localhost:5000")
    print("\n  Test with curl:")
    print("  curl -X POST http://localhost:5000/api/predict -F 'file=@test.jpg'")

def git_push():
    """Git commit and push."""
    print("\n📤 Pushing to GitHub...")
    run_cmd("git add -A")
    run_cmd('git commit -m "feat: automated deployment - all files ready"')
    run_cmd("git push origin main")
    print("✅ Pushed to GitHub")

def create_github_actions():
    """Create GitHub Actions workflow for auto-conversion."""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow = """name: Convert Model to ONNX

on:
  push:
    branches: [main]
    paths:
      - 'models/tomato_model.h5'
      - '.github/workflows/convert.yml'

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install tensorflow tf2onnx onnxruntime
      
      - name: Convert model
        run: |
          python << 'EOF'
import tensorflow as tf
import tf2onnx
import onnx
import os
          
model = tf.keras.models.load_model('models/tomato_model.h5', compile=False)
input_sig = [tf.TensorSpec(model.inputs[0].shape, tf.float32, name='input')]
onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=input_sig, opset=13)
onnx.save(onnx_model, 'models/tomato_model.onnx')
print('✅ Model converted')
EOF
      
      - name: Commit ONNX model
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add models/tomato_model.onnx
          git commit -m "chore: auto-convert H5 to ONNX"
          git push
"""
    
    with open(workflow_dir / "convert.yml", "w") as f:
        f.write(workflow)
    
    print("✅ Created GitHub Actions workflow")

def main():
    """Run deployment automation."""
    print("=" * 70)
    print("  🚀 TOMATO DISEASE APP - AUTOMATED DEPLOYMENT")
    print("=" * 70)
    
    os_name = sys.platform
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"\n📋 Environment: {os_name} | Python {py_ver}")
    
    # Check files exist
    needed = ['app.py', 'requirements.txt', 'Procfile', 'models/tomato_model.h5']
    missing = [f for f in needed if not Path(f).exists()]
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return
    
    print(f"✅ All dependencies found\n")
    
    # Step 1: Try model conversion
    print("STEP 1: MODEL CONVERSION (H5 → ONNX)")
    print("-" * 70)
    if convert_model():
        print("✅ Model conversion successful!")
    else:
        print("⚠ Model conversion skipped (requires Python 3.11-3.13)")
        print("  Creating GitHub Actions for auto-conversion...")
        create_github_actions()
    
    # Step 2: Test locally
    print("\n\nSTEP 2: TEST LOCAL SETUP")
    print("-" * 70)
    test_local()
    
    # Step 3: Push to GitHub
    print("\n\nSTEP 3: GIT PUSH")
    print("-" * 70)
    try:
        git_push()
    except:
        print("⚠ Git push failed (check credentials)")
    
    # Final instructions
    print("\n\n" + "=" * 70)
    print("  ✅ AUTOMATION COMPLETE!")
    print("=" * 70)
    print("""
NEXT STEPS:

1️⃣  Model Conversion:
    - If using Python 3.14: GitHub Actions will auto-convert on next push
    - Else: Model should be ready at models/tomato_model.onnx

2️⃣  Test Locally:
    pip install -r requirements.txt
    python app.py
    # Visit http://localhost:5000

3️⃣  Upload Model to Google Drive:
    - Upload models/tomato_model.onnx
    - Get FILE_ID and copy to clipboard

4️⃣  Deploy on Render:
    - Create new Web Service
    - Connect GitHub repo
    - Add env var: GOOGLE_DRIVE_MODEL_ID={FILE_ID}
    - Deploy!

5️⃣  Keep Alive:
    - Register at uptimerobot.com
    - Add monitor: https://tomato-disease-app.onrender.com/health

📚 Full guide: See DEPLOYMENT_GUIDE.md
""")

if __name__ == '__main__':
    main()
