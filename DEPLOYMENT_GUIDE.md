# 🚀 Complete Deployment Guide

**Status**: All merge conflicts fixed ✅ | Backend ready ✅ | Mobile app ready ✅

---

## PHASE 1: LOCAL MODEL CONVERSION (Do This First)

### 1.1 Install Conversion Tools

```bash
pip install tf2onnx tensorflow onnxruntime
```

### 1.2 Convert H5 Model to ONNX

Create a file `convert_model.py`:

```python
import tensorflow as tf
import tf2onnx
import onnx
import os

# Load your existing model
model = tf.keras.models.load_model('models/tomato_model.h5', compile=False)
print('Model input shape:', model.input_shape)

# Create input signature (matches your model's input)
input_sig = [tf.TensorSpec(model.inputs[0].shape, tf.float32, name='input')]

# Convert to ONNX
print('Converting to ONNX...')
onnx_model, _ = tf2onnx.convert.from_keras(
    model, 
    input_signature=input_sig, 
    opset=13
)

# Save the converted model
onnx.save(onnx_model, 'models/tomato_model.onnx')
model_size = os.path.getsize('models/tomato_model.onnx') / (1024 * 1024)
print(f'✓ Converted successfully! Size: {model_size:.1f} MB')
```

Run it:
```bash
python convert_model.py
```

### 1.3 Verify ONNX Model Works

```python
import onnxruntime as ort
import numpy as np

sess = ort.InferenceSession('models/tomato_model.onnx')
input_name = sess.get_inputs()[0].name

# Test with dummy input
dummy = np.random.randn(1, 224, 224, 3).astype(np.float32)
outputs = sess.run(None, {input_name: dummy})

print('Output shape:', outputs[0].shape)  # Should be (1, 10)
print('✓ ONNX model verified successfully!')
```

---

## PHASE 2: TEST LOCALLY

### 2.1 Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Run Flask Backend

```bash
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * WARNING: This is a development server. Do not use it in production directly.
ONNX model loaded from models/tomato_model.onnx
```

### 2.4 Test Web Interface

1. Open browser: **http://localhost:5000**
2. Upload a tomato leaf image
3. See prediction with confidence score

### 2.5 Test REST API

```bash
# Using curl (Windows PowerShell)
$filepath = "C:\path\to\tomato_leaf.jpg"
curl -X POST http://localhost:5000/api/predict `
  -F "file=@$filepath" `
  -H "Accept: application/json"

# Using Python
import requests
files = {'file': open('tomato_leaf.jpg', 'rb')}
r = requests.post('http://localhost:5000/api/predict', files=files)
print(r.json())
```

**Expected response:**
```json
{
  "filename": "leaf.jpg",
  "prediction": "Early_blight",
  "confidence": 0.9437,
  "mask": "<base64 PNG>",
  "all_predictions": {
    "Bacterial_spot": 0.0012,
    "Early_blight": 0.9437,
    ...
  }
}
```

---

## PHASE 3: PREPARE FOR PRODUCTION

### 3.1 Upload Model to Google Drive

1. Go to https://drive.google.com
2. Create a folder "tomato-models" (optional)
3. Upload `models/tomato_model.onnx`
4. Right-click on file → Share
5. Change permission to "Anyone with the link can view"
6. Copy the file ID from the URL:
   ```
   https://drive.google.com/file/d/{FILE_ID}/view
   ```
7. **Save this FILE_ID** - you'll need it later

### 3.2 Git: Commit and Push

```bash
# Check status
git status

# Add all updated files
git add app.py requirements.txt Procfile render.yaml download_model.py .gitignore README.md
git add mobile_app/

# Commit with message
git commit -m "fix: resolve conflicts, replace tensorflow with onnxruntime, production ready"

# Push to main branch
git push origin main
```

**You should see these files tracked:**
- ✅ app.py (clean, no conflict markers)
- ✅ requirements.txt (no tensorflow)
- ✅ Procfile
- ✅ render.yaml
- ✅ download_model.py
- ✅ .gitignore (model files excluded)
- ✅ README.md (production docs)
- ✅ mobile_app/ (entire folder)

---

## PHASE 4: DEPLOY TO RENDER.COM

### 4.1 Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (easiest)
3. Authorize GitHub access

### 4.2 Create Web Service

1. Click **New** → **Web Service**
2. Select your `tomato-diseace-identification` repository
3. Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | tomato-disease-app |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT` |
| **Plan** | Free |

4. Click **Create Web Service**

### 4.3 Set Environment Variables

In the Render dashboard, go to your service → **Environment**:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | 3.10.0 |
| `MODEL_PATH` | models/tomato_model.onnx |
| `DEBUG_MODE` | false |
| `CONF_THRESH` | 0.6 |
| `GOOGLE_DRIVE_MODEL_ID` | **{PASTE YOUR FILE_ID HERE}** |

**Save changes** - Render will redeploy automatically

### 4.4 Wait for Deployment

Render will:
1. Clone your repo
2. Install dependencies
3. Auto-download model from Google Drive
4. Start the Flask app

Watch the build logs until you see:
```
ONNX model loaded from models/tomato_model.onnx
✓ Deployment successful!
```

**Your live URL will be:** `https://tomato-disease-app.onrender.com`

---

## PHASE 5: VERIFY PRODUCTION

### 5.1 Health Check

```bash
curl https://tomato-disease-app.onrender.com/health
```

**Expected:**
```json
{"status":"ok","model":"loaded","version":"1.0.0"}
```

### 5.2 Test Web UI

Open in browser: https://tomato-disease-app.onrender.com
- Upload an image
- See prediction

### 5.3 Test REST API

```bash
# Using curl
curl -X POST https://tomato-disease-app.onrender.com/api/predict \
  -F "file=@tomato_leaf.jpg"

# Using Python
import requests
files = {'file': open('tomato_leaf.jpg', 'rb')}
r = requests.post('https://tomato-disease-app.onrender.com/api/predict', files=files)
print(r.json())
```

---

## PHASE 6: KEEP APP AWAKE (Free Tier Only)

Render stops free apps after 15 minutes of inactivity. Use UptimeRobot to ping it:

### 6.1 Create UptimeRobot Monitor

1. Go to https://uptimerobot.com
2. Sign up (free account)
3. Click **Add Monitor**
4. Fill in:
   - **Monitor Type**: HTTP(s)
   - **URL**: `https://tomato-disease-app.onrender.com/health`
   - **Interval**: 5 minutes

5. Click **Create Monitor**

**Result:** Your app is pinged every 5 minutes → Stays awake 24/7 ✅

---

## PHASE 7: DEPLOY MOBILE APP

### 7.1 Update Backend URL

Edit `mobile_app/App.js` line ~15:

```javascript
// UPDATE THIS to your Render URL
const BACKEND_URL = 'https://tomato-disease-app.onrender.com';
```

### 7.2 Test with Expo Go (No Build)

```bash
cd mobile_app
npm install
npx expo start
```

**In terminal, see a QR code:**
- Scan with **Expo Go** app (download free from app store)
- Or press `a` for Android or `i` for iOS simulator

### 7.3 Build Standalone APK (Optional)

If you want to share a single `.apk` file:

```bash
npm install -g eas-cli
eas login
cd mobile_app
eas build:configure
eas build -p android --profile preview
```

This generates an `.apk` file anyone can install.

---

## PHASE 8: FINAL CHECKLIST

- [ ] ONNX model created: `models/tomato_model.onnx` exists ✅
- [ ] `requirements.txt` has NO tensorflow ✅
- [ ] `app.py` uses ONNX, NOT TensorFlow ✅
- [ ] Merge conflicts removed (no `<<<<`, `====`, `>>>>`) ✅
- [ ] All files committed and pushed to GitHub ✅
- [ ] Render service created and running ✅
- [ ] `GOOGLE_DRIVE_MODEL_ID` environment variable set ✅
- [ ] Health check returns 200 OK ✅
- [ ] Web UI works at https://domain.onrender.com ✅
- [ ] REST API works: POST to /api/predict ✅
- [ ] UptimeRobot monitor created ✅
- [ ] Mobile app tested with Expo Go ✅

---

## COMMON ISSUES & SOLUTIONS

### "Model not found"
```
Error: Model load failed: No such file
```
**Solution:**
1. Check `GOOGLE_DRIVE_MODEL_ID` is set in Render
2. Verify file is shared publicly on Google Drive
3. Check Drive file ID is correct

### "Prediction fails with 'Image does not contain a leaf'"
**Solution:**
- Upload a clearer leaf photo
- Or adjust HSV thresholds at `/admin`

### "Mobile app won't connect to backend"
**Solution:**
1. Verify URL in `mobile_app/App.js`
2. Test backend is running: `curl https://domain.onrender.com/health`
3. For local testing, use ngrok: `npx ngrok http 5000`

### "Build command times out"
**Solution:**
- Try increasing Render's build timeout
- Or pre-download model to avoid timeout

---

## DEPLOYMENT SUMMARY

| Component | Status | Location |
|-----------|--------|----------|
| Flask Backend | ✅ Ready | https://tomato-disease-app.onrender.com |
| ONNX Model | ✅ Converted | Google Drive (auto-downloaded) |
| Web UI | ✅ Ready | https://tomato-disease-app.onrender.com |
| REST API | ✅ Ready | POST /api/predict |
| Mobile App | ✅ Ready | Expo Go / Android APK |
| Database | ❌ N/A | Log files only |

---

## NEXT STEPS

1. **NOW**: Convert your H5 model to ONNX (5 min)
2. **TODAY**: Push to GitHub and deploy on Render (10 min)
3. **VERIFY**: Test web UI and API (5 min)
4. **MOBILE**: Test Expo app (5 min)
5. **MONITOR**: Set up UptimeRobot (2 min)

**Total Time: ~30 minutes to full production deployment**

---

**Questions?** See [README.md](README.md) → Troubleshooting section
