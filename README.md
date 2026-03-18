# 🍅 Tomato Disease Identification System

An AI-powered full-stack application for identifying tomato leaf diseases using deep learning. Includes a Flask backend with ONNX inference, responsive web UI, and cross-platform mobile app built with Expo React Native.

**Live Demo:** https://tomato-disease-app.onrender.com

## 🎯 Features

- **Web Interface**: Upload tomato leaf images and get instant AI diagnosis
- **Mobile App**: Native iOS and Android app via Expo for field use
- **10 Disease Classes**: Bacterial spot, Early blight, Late blight, Leaf mold, Septoria leaf spot, Spider mites, Target spot, Yellow leaf curl virus, Mosaic virus, and Healthy
- **High Accuracy**: InceptionV3 model trained on PlantVillage dataset (224×224 input)
- **Confidence Scoring**: Get probability distribution across all disease classes
- **Treatment Tips**: Actionable recommendations for each detected disease
- **Green Leaf Detection**: Visual mask showing detected leaf regions
- **Admin Dashboard**: Tune HSV thresholds for leaf detection

## 📁 Project Structure

```
tomato-diseace-identification/
├── app.py                       # Flask backend (ONNX inference)
├── download_model.py            # Auto-download model from Google Drive
├── requirements.txt             # Python dependencies
├── Procfile                     # Render deployment config
├── render.yaml                  # Render service definition
├── .gitignore                   # Git ignore patterns
│
├── models/
│   ├── tomato_model.h5         # Original TensorFlow model (you have this)
│   └── tomato_model.onnx       # Converted ONNX model (need to create)
│
├── mobile_app/                  # Expo React Native mobile app
│   ├── App.js                   # Main component with camera & API calls
│   ├── app.json                 # Expo configuration
│   ├── package.json             # Dependencies
│   └── README.md                # Mobile app setup instructions
│
├── static/
│   ├── style.css                # Web UI styling
│   └── uploads/                 # Temporary uploaded image storage
│
├── templates/
│   ├── tomato-disease-organic.html  # Main web UI
│   ├── admin.html               # Admin dashboard
│   ├── preview.html             # Image preview page
│   ├── 404.html                 # Error pages
│   └── 500.html
│
├── tests/                       # Test files
└── README.md                    # This file
```

## 🚀 Quick Start

### Local Development (Web)

1. **Create Python environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Convert model (one-time):**
   ```bash
   # See "Model Conversion" section below
   ```

4. **Run Flask app:**
   ```bash
   python app.py
   ```
   Open browser: http://localhost:5000

### Mobile App Development

See [mobile_app/README.md](mobile_app/README.md) for:
- Expo Go quick testing (no build needed)
- Building standalone Android APK
- Building iOS app

## 🔄 Model Conversion: H5 → ONNX

Your existing `models/tomato_model.h5` must be converted to ONNX format for production deployment.

### Step 1: Install conversion tools
```bash
pip install tf2onnx tensorflow onnxruntime
```

### Step 2: Convert the model
```python
import tensorflow as tf
import tf2onnx
import onnx
import os

# Load your trained model
model = tf.keras.models.load_model('models/tomato_model.h5', compile=False)
print('Model input shape:', model.input_shape)

# Convert to ONNX
input_sig = [tf.TensorSpec(model.inputs[0].shape, tf.float32, name='input')]
onnx_model, _ = tf2onnx.convert.from_keras(
    model, 
    input_signature=input_sig, 
    opset=13
)

# Save converted model
onnx.save(onnx_model, 'models/tomato_model.onnx')
print('✓ Converted! Size:', round(os.path.getsize('models/tomato_model.onnx')/1024/1024, 1), 'MB')
```

### Step 3: Verify ONNX model
```python
import onnxruntime as ort
import numpy as np

sess = ort.InferenceSession('models/tomato_model.onnx')
dummy = np.random.randn(1, 224, 224, 3).astype(np.float32)
out = sess.run(None, {sess.get_inputs()[0].name: dummy})
print('Output shape:', out[0].shape)  # Should be (1, 10)
print('✓ ONNX verified OK')
```

**Expected model size:** ~20-50 MB (much smaller than H5)

## 🌐 Deployment on Render.com

### Prerequisites
- GitHub account with this repo pushed
- Google Drive account (for model hosting)
- Render.com account (free)

### Step 1: Upload ONNX Model to Google Drive

1. Go to Google Drive
2. Upload `models/tomato_model.onnx`
3. Right-click → Share → Change to "Anyone with link can view"
4. Copy the file ID from URL: `https://drive.google.com/file/d/{FILE_ID}/view`

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) → Dashboard
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Fill in settings:
   - **Name:** tomato-disease-app
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT`
   - **Plan:** Free

5. Add environment variables:
   - `PYTHON_VERSION` = `3.10.0`
   - `MODEL_PATH` = `models/tomato_model.onnx`
   - `DEBUG_MODE` = `false`
   - `CONF_THRESH` = `0.6`
   - `GOOGLE_DRIVE_MODEL_ID` = (paste your file ID here)

6. Click **Deploy** and wait ~5 minutes

### Step 3: Verify Deployment

```bash
# Health check
curl https://tomato-disease-app.onrender.com/health
# Expected: {"status":"ok","model":"loaded","version":"1.0.0"}

# Test prediction
curl -X POST https://tomato-disease-app.onrender.com/api/predict \
  -F "file=@tomato_leaf.jpg"
```

### Step 4: Keep App Awake (Free Tier)

Render stops free apps after 15 mins of inactivity. Use UptimeRobot to ping it:

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up (free)
3. Add Monitor:
   - Type: HTTP(s)
   - URL: `https://tomato-disease-app.onrender.com/health`
   - Interval: 5 minutes
4. Save → Your app stays awake 24/7!

## 📱 Mobile App Configuration

In `mobile_app/App.js`, update the backend URL to your Render domain:

```javascript
const BACKEND_URL = 'https://tomato-disease-app.onrender.com';
```

For local testing with ngrok:
```bash
npx ngrok http 5000
# Copy the https://... URL and paste in App.js
```

## 🏥 Disease Classes

| ID | Disease | Characteristics |
|----|---------|-----------------|
| 0 | Bacterial Spot | Small dark lesions with water-soaked appearance |
| 1 | Early Blight | Brown concentric rings on older leaves |
| 2 | Late Blight | Water-soaked spots, white fungal growth underneath |
| 3 | Leaf Mold | Yellow patches on top, gray-brown mold on bottom |
| 4 | Septoria Leaf Spot | Small circular spots with concentric rings |
| 5 | Spider Mites | Yellow stippling, fine webbing |
| 6 | Target Spot | Circular spots with concentric rings near stem |
| 7 | Yellow Leaf Curl Virus | Yellowing and upward leaf curling |
| 8 | Mosaic Virus | Mottled green and yellow patches |
| 9 | Healthy | No visible disease symptoms |

## 🔧 API Endpoints

### Web UI
- `GET /` - Main upload interface
- `POST /` - Submit image via form

### REST API (Mobile/External)
- `POST /api/predict` - Submit image, get prediction

**Request:**
```bash
curl -X POST https://tomato-disease-app.onrender.com/api/predict \
  -F "file=@leaf.jpg"
```

**Response:**
```json
{
  "filename": "leaf.jpg",
  "prediction": "Early_blight",
  "confidence": 0.9437,
  "mask": "<base64 PNG>",
  "all_predictions": {
    "Bacterial_spot": 0.0012,
    "Early_blight": 0.9437,
    "Late_blight": 0.0234,
    ...
  }
}
```

### Health Check
- `GET /health` - Service status

**Response:**
```json
{
  "status": "ok",
  "model": "loaded",
  "version": "1.0.0"
}
```

### Admin API
- `GET /api/admin/config` - Get current HSV thresholds
- `POST /api/admin/config` - Update HSV thresholds (JSON body)

## ⚙️ Configuration via Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Server port |
| `MODEL_PATH` | models/tomato_model.onnx | Path to ONNX model |
| `DEBUG_MODE` | false | Enable debug logging |
| `CONF_THRESH` | 0.6 | Confidence threshold (0-1) |
| `GREEN_H_MIN` | 25 | Min hue for green |
| `GREEN_H_MAX` | 100 | Max hue for green |
| `S_MIN` | 40 | Min saturation |
| `V_MIN` | 40 | Min value |
| `GREEN_PROP_THRESH` | 0.03 | Min green pixel proportion |
| `GOOGLE_DRIVE_MODEL_ID` | - | Google Drive model file ID |

## 🧪 Testing

### Web Interface
1. Open frontend: http://localhost:5000
2. Upload a tomato leaf image
3. See prediction and mask overlay

### REST API
```bash
# Using Python
python -c "
import requests
files = {'file': open('test_leaf.jpg', 'rb')}
r = requests.post('http://localhost:5000/api/predict', files=files)
print(r.json())
"

# Using curl
curl -X POST http://localhost:5000/api/predict \
  -F 'file=@test_leaf.jpg' \
  -H 'Accept: application/json'
```

### Admin Dashboard
1. Open: http://localhost:5000/admin
2. Adjust HSV thresholds
3. Test leaf detection on sample images

## 📊 Model Info

- **Architecture**: InceptionV3 (pre-trained on ImageNet, fine-tuned on PlantVillage)
- **Input**: 224×224 RGB image
- **Output**: 10 class probabilities
- **Framework**: TensorFlow/Keras → ONNX
- **Size**: ~20-50 MB (ONNX format)
- **Speed**: <100ms per prediction (CPU)

## 🐛 Troubleshooting

### Model not loading
```
Error: Model not found on server
```
- Ensure `models/tomato_model.onnx` exists locally
- Check `GOOGLE_DRIVE_MODEL_ID` environment variable on Render
- Verify Google Drive file is shared publicly

### "Image does not contain a leaf"
- Upload a clear, well-lit leaf photo
- Ensure the leaf is the main focus
- Adjust HSV thresholds in `/admin` if needed

### Mobile app won't connect
- Verify backend URL in `mobile_app/App.js`
- Check backend is running: `curl https://domain.onrender.com/health`
- Use ngrok for local testing: `npx ngrok http 5000`

### Predictions unreliable
- Model performs best on PlantVillage dataset images
- Use high-quality, well-lit leaf photos
- Ensure image shows disease symptoms clearly

## 📚 Training Your Own Model

To train a custom model:

```bash
python leaf_detector/train_detector.py
```

Then convert and deploy as described above.

## 📄 License

MIT - See LICENSE file

## 🙏 Acknowledgments

- **Model**: InceptionV3, pre-trained on ImageNet
- **Dataset**: PlantVillage (tomato subset)
- **Framework**: TensorFlow/Keras, ONNX Runtime
- **Mobile**: Expo, React Native
- **Backend**: Flask, Gunicorn
- **Hosting**: Render.com

## 📞 Support

For issues or questions:
1. Check [troubleshooting](#-troubleshooting) section
2. Review logs: `tail -f /var/log/render.log` (Render)
3. Test locally first: `python app.py`
4. Check API with curl/Postman

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**Status**: Production Ready ✅
