# ⚡ Quick Copy-Paste Commands

## 1. CONVERT MODEL (Run Locally First)

```bash
# Install tools
pip install tf2onnx tensorflow onnxruntime

# Convert H5 to ONNX
python << 'EOF'
import tensorflow as tf
import tf2onnx, onnx, os

model = tf.keras.models.load_model('models/tomato_model.h5', compile=False)
print('Input shape:', model.input_shape)

input_sig = [tf.TensorSpec(model.inputs[0].shape, tf.float32, name='input')]
onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=input_sig, opset=13)
onnx.save(onnx_model, 'models/tomato_model.onnx')
print('✓ Converted! Size:', round(os.path.getsize('models/tomato_model.onnx')/1024/1024, 1), 'MB')
EOF

# Verify
python << 'EOF'
import onnxruntime as ort
import numpy as np

sess = ort.InferenceSession('models/tomato_model.onnx')
dummy = np.random.randn(1, 224, 224, 3).astype(np.float32)
out = sess.run(None, {sess.get_inputs()[0].name: dummy})
print('Output shape:', out[0].shape)
print('✓ ONNX verified OK')
EOF
```

## 2. TEST LOCALLY

```bash
# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Run
python app.py

# Test in browser: http://localhost:5000
# Or test API with curl:
curl -X POST http://localhost:5000/api/predict -F "file=@test_leaf.jpg"
```

## 3. GIT: COMMIT & PUSH

```bash
git add app.py requirements.txt Procfile render.yaml download_model.py .gitignore README.md
git add mobile_app/
git commit -m "fix: resolve conflicts, tensorflow->onnx, production ready"
git push origin main
```

## 4. GOOGLE DRIVE: GET MODEL FILE ID

After uploading `models/tomato_model.onnx` to Google Drive:

```
URL: https://drive.google.com/file/d/{YOUR_FILE_ID}/view
                                      ^^^^^^^^^^^^^^
                                      COPY THIS
```

Right-click file → Share → "Anyone with link" ✓

## 5. RENDER.COM: DEPLOY

**Manual:** 
1. Go to https://render.com → Dashboard
2. New → Web Service
3. Connect GitHub repo: `tomato-diseace-identification`
4. Name: `tomato-disease-app`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT`
7. Add Env Vars (see below)
8. Deploy

**Environment Variables to Add:**
```
PYTHON_VERSION = 3.10.0
MODEL_PATH = models/tomato_model.onnx
DEBUG_MODE = false
CONF_THRESH = 0.6
GOOGLE_DRIVE_MODEL_ID = {PASTE_YOUR_FILE_ID_HERE}
```

## 6. VERIFY DEPLOYMENT

```bash
# Health check
curl https://tomato-disease-app.onrender.com/health

# Web UI
Open: https://tomato-disease-app.onrender.com

# API test
curl -X POST https://tomato-disease-app.onrender.com/api/predict \
  -F "file=@test_leaf.jpg"
```

## 7. KEEP ALIVE (UptimeRobot)

1. https://uptimerobot.com
2. Sign up
3. Add Monitor:
   - Type: HTTP(s)
   - URL: `https://tomato-disease-app.onrender.com/health`
   - Interval: 5 min
4. Save

## 8. MOBILE APP

```bash
# Update backend URL in mobile_app/App.js:
const BACKEND_URL = 'https://tomato-disease-app.onrender.com';

# Test with Expo Go
cd mobile_app
npm install
npx expo start
# Scan QR code with Expo Go app (iOS) or press A (Android)

# Build standalone APK
npm install -g eas-cli
eas login
eas build:configure
eas build -p android --profile preview
```

---

## ✅ VERIFICATION CHECKLIST

```bash
# 1. Model
ls -la models/tomato_model.onnx  # Should exist

# 2. Requirements (no tensorflow)
grep -i tensorflow requirements.txt  # Should return nothing

# 3. App file (no conflict markers)
grep -E '<<<<<<|=======|>>>>>>>' app.py  # Should return nothing

# 4. Git status clean
git status  # All committed

# 5. Backend health
curl https://tomato-disease-app.onrender.com/health
# {"status":"ok","model":"loaded","version":"1.0.0"}
```

---

## FILE CONTENTS READY TO USE

### requirements.txt ✅
```
flask==2.3.3
flask-cors==4.0.0
onnxruntime==1.17.1
numpy==1.26.4
pillow==10.3.0
werkzeug==3.0.3
requests==2.31.0
gunicorn==22.0.0
gdown==5.1.0
opencv-python-headless==4.9.0.80
```

### Procfile ✅
```
web: gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT
```

### Disease Classes ✅
```
0 = Bacterial_spot
1 = Early_blight
2 = Late_blight
3 = Leaf_Mold
4 = Septoria_leaf_spot
5 = Spider_mites
6 = Target_Spot
7 = Yellow_Leaf_Curl_Virus
8 = Mosaic_virus
9 = Healthy
```

---

## EXPECTED TIMING

| Step | Time |
|------|------|
| Convert model | 2 min |
| Test locally | 5 min |
| Git push | 1 min |
| Render deploy | 5 min |
| Verify | 3 min |
| UptimeRobot | 2 min |
| Mobile test | 3 min |
| **TOTAL** | **~20 min** |

---

## SUPPORT

- Model conversion issues → See DEPLOYMENT_GUIDE.md
- API errors → Check logs: `curl -v https://...`  
- Mobile problems → Update URL in App.js, re-run expo start
- Model not found → Verify GOOGLE_DRIVE_MODEL_ID env var
