# Render Deployment Guide — Tomato Disease Identification

This guide walks you through deploying the Flask-based tomato disease identification app to Render (free tier or paid).

---

## 📋 Project Overview

- **Framework**: Flask + TensorFlow (InceptionV3)
- **Model**: `models/tomato_model.h5` (Keras H5 format)
- **Endpoints**:
  - `GET /` — Web UI (HTML form to upload leaf images)
  - `POST /api/predict` — JSON API for ML clients/mobile apps
  - `GET /health` — Health check endpoint
  - `GET /admin` / `POST /admin` — Admin UI to tune HSV thresholds
- **Static Assets**: `static/` (CSS, uploaded images)
- **Templates**: `templates/index.html`, `admin.html`, `preview.html`

---

## 🔧 Deployment Configuration Files

### 1. **runtime.txt** — Python Version
```
python-3.10.13
```
- **Why 3.10?** TensorFlow 2.13.0 has excellent support for Python 3.8–3.11.
- Python 3.10 balances stability and modern language features.
- Render fully supports this version on the free tier.

### 2. **requirements.txt** — Python Dependencies
```
tensorflow==2.13.0
numpy==1.24.3
Pillow==10.0.0
opencv-python-headless==4.8.0.76
gradio==3.50.2
Flask==2.0.1
flask-cors==3.0.10
werkzeug==2.0.2
gunicorn==20.1.0
requests==2.31.0
```
- All pinned to tested versions for stability.
- `opencv-python-headless` (no GUI/X11 overhead) for production.
- `gunicorn` — production WSGI server.

### 3. **Procfile** — Gunicorn Web Process
```
web: gunicorn --bind 0.0.0.0:$PORT --worker-class gthread --workers ${GUNICORN_WORKERS:-1} --threads ${GUNICORN_THREADS:-4} --timeout ${GUNICORN_TIMEOUT:-120} app:app
```

#### **Why This Configuration for ML Inference?**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `--bind 0.0.0.0:$PORT` | `0.0.0.0:PORT` | Listen on all interfaces; use Render's dynamic PORT env var. |
| `--worker-class gthread` | Thread-based, not process-based | Avoids spawning multiple processes, each loading the TensorFlow model separately (huge memory waste). |
| `--workers 1` (default) | Single OS process | One model instance in memory; multiple threads share it. Fine for free tier; can increase to 2–4 for paid. |
| `--threads 4` (default) | 4 Python threads per worker | Handles up to 4 concurrent requests without blocking. Adjust: `--threads 8` for paid tier or less CPU contention. |
| `--timeout 120` (default) | 120 seconds | InceptionV3 inference + image preprocessing typically takes 1–5s. 120s is safe for slow cold starts. Reduce to 60 for faster response times. |

#### **Environment Variables (Optional Overrides)**
Set these in your Render service environment to tune at runtime without redeploying:

```bash
GUNICORN_WORKERS=1          # Increase only if NOT on free tier (costs more memory)
GUNICORN_THREADS=4          # Increase for higher throughput (4–8 recommended)
GUNICORN_TIMEOUT=120        # Reduce to 60 if cold starts are fast
```

### 4. **render.yaml** — Infrastructure as Code
```yaml
services:
  - type: web
    name: tomato-disease-detector
    env: python
    plan: free
    region: oregon
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --worker-class gthread --workers ${GUNICORN_WORKERS:-1} --threads ${GUNICORN_THREADS:-4} --timeout ${GUNICORN_TIMEOUT:-120} app:app
    envVars:
      - key: MODEL_URL
        value: ""
        sync: false
```

---

## 🚀 Deployment Steps

### **Option 1: Render Dashboard (Recommended for Beginners)**

1. Go to [render.com](https://render.com) and sign up with GitHub.
2. Click **New +** → **Web Service**.
3. Select your GitHub repository (`tomato-diseace-identification`).
4. Fill in the form:
   - **Name**: `tomato-disease-detector`
   - **Environment**: `Python`
   - **Plan**: `Free` (or paid if you want better performance)
   - **Region**: `Oregon` (or closest to you)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt` (Render auto-detects if not specified)
   - **Start Command**: Copy from [Procfile](Procfile)
5. Click **Create Web Service**.
6. Render will automatically deploy on every push to `main`.
7. Visit your service URL: `https://tomato-disease-detector.onrender.com` (your custom URL).

### **Option 2: Connect via render.yaml (Infrastructure as Code)**

If Render detects `render.yaml` in the repo root, it will use it instead of the dashboard form:

1. Push the repo with `render.yaml` to GitHub.
2. Go to Render dashboard → **Blueprints** → **New Blueprint**.
3. Select the repo and authorize.
4. Render reads `render.yaml` and creates the service automatically.
5. No additional configuration needed (unless you add env-specific overrides).

### **Option 3: GitHub Actions Workflow (CI/CD Auto-Deploy)**

The workflow file `.github/workflows/deploy_render.yml` is included. To enable it:

1. In your GitHub repo, go **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Add two secrets:
   - `RENDER_API_KEY`: Get from Render dashboard (Account Settings → API Keys).
   - `RENDER_SERVICE_ID`: After creating the service, copy the service ID from the URL or API.
3. Every push to `main` will trigger the workflow, which calls the Render API to deploy.

---

## 🌍 Environment Variables & Configuration

### **Critical for Production**

1. **Flask Debug Mode** (must be off in production):
   ```bash
   FLASK_ENV=production
   ```
   - Render sets this by default.

2. **Model Loading** (if hosting model externally):
   ```bash
   MODEL_URL=https://your-bucket.s3.amazonaws.com/tomato_model.h5
   ```
   - Leave empty if model is in the repo (recommended for simplicity).
   - If set, the app will attempt to download the model at startup.

3. **HSV Threshold Tuning** (for leaf detection):
   ```bash
   GREEN_H_MIN=25
   GREEN_H_MAX=100
   S_MIN=40
   V_MIN=40
   GREEN_PROP_THRESH=0.03
   CONF_THRESH=0.4
   ```
   - These defaults are tuned for the app. Adjust if needed via `/admin` UI or set env vars.

### **Optional (Performance Tuning)**

- `GUNICORN_WORKERS=1` — Leave at 1 for free tier; increase to 2–4 for paid.
- `GUNICORN_THREADS=4` — Increase to 8 if you expect high concurrent traffic.
- `GUNICORN_TIMEOUT=120` — Reduce to 60 if inference is consistently fast.

---

## ✅ Testing & Validation

### **Local Testing (Before Deploy)**

1. **Activate venv**:
   ```bash
   .venv\Scripts\Activate.ps1  # Windows
   # or
   source .venv/bin/activate   # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally with Gunicorn**:
   ```bash
   gunicorn --bind 127.0.0.1:8000 --worker-class gthread --workers 1 --threads 4 --timeout 120 app:app
   ```
   - Visit `http://localhost:8000/` and upload a test leaf image.
   - Verify `/health` returns `{"status": "ok"}`.
   - Verify `/api/predict` accepts POST with an image file.

4. **Check model loads**:
   ```bash
   python -c "import tensorflow as tf; model = tf.keras.models.load_model('models/tomato_model.h5'); print('Model loaded OK')"
   ```

### **Post-Deploy Checks**

After Render deploys:

1. **Health Check**:
   ```bash
   curl https://<your-render-url>/health
   ```
   Expected: `{"status":"ok"}`

2. **Web UI**:
   - Visit `https://<your-render-url>/`
   - Upload a tomato leaf image and verify prediction works.

3. **API Test**:
   ```bash
   curl -X POST https://<your-render-url>/api/predict \
     -F "file=@path/to/leaf.jpg"
   ```

4. **Logs**:
   - In Render dashboard → your service → **Logs** tab.
   - Check for any TensorFlow model loading errors or warnings.

---

## 📊 Performance & Scaling

### **Free Tier Constraints**
- **Memory**: 512 MB (shared with model, memory can be tight).
- **CPU**: Shared vCPU (inference may take 2–5 seconds).
- **Concurrency**: 1 request at a time on free tier (gthread helps, but single worker is bottleneck).
- **Cold Starts**: ~20–30 seconds on first request after long inactivity (model loads from disk).

### **Scaling Tips**

| Issue | Solution |
|-------|----------|
| **"Killed" errors (OOM)** | Upgrade to paid tier (1GB+ RAM) or reduce model size (quantization). |
| **Slow inference** | Increase `GUNICORN_THREADS` to 8; cache model in memory (already done). |
| **Long cold starts** | Model is large (~95 MB H5 file). Consider TensorFlow Lite (`.tflite`, ~30 MB) for mobile clients. |
| **Many concurrent users** | Upgrade to paid; consider load balancing or CDN caching. |

### **Optimization Ideas**

1. **Model Quantization**: Convert `tomato_model.h5` to `tomato_model.tflite` for mobile/embedded (faster, smaller).
2. **Model Pruning**: Remove non-essential layers; can reduce model size by 20–30%.
3. **Caching**: The app already uses `functools.lru_cache` for model loading — good!
4. **Static File CDN**: Serve `static/` from a CDN (e.g., Render's built-in CDN) to reduce server load.

---

## 🔐 Security & Best Practices

1. **Do NOT hardcode secrets**:
   - Use Render environment variables for API keys, model URLs, etc.
   - Example: `MODEL_URL` should be a secret in Render, not in the code.

2. **CORS Policy**:
   - The app has `flask_cors` enabled. Verify it's restrictive enough for your use case.
   - Update `CORS(app)` to whitelist specific domains if needed.

3. **File Upload Safety**:
   - App uses `werkzeug.secure_filename` to prevent path traversal. ✅
   - Max upload size: 16 MB (reasonable for images). ✅
   - Consider adding virus scanning (ClamAV) for production.

4. **Admin Panel Access**:
   - `/admin` endpoint has no authentication. Add basic auth if deployed publicly:
     ```python
     from flask_basicauth import BasicAuth
     app.config['BASIC_AUTH_USERNAME'] = 'admin'
     app.config['BASIC_AUTH_PASSWORD'] = os.getenv('ADMIN_PASSWORD')
     basic_auth = BasicAuth(app)
     @app.route('/admin')
     @basic_auth.login_required
     def admin_page():
       ...
     ```

---

## 📞 Troubleshooting

### **"Model not found" error**
- Ensure `models/tomato_model.h5` exists in the repo before deploy.
- If using `MODEL_URL`, verify the URL is accessible and the link is correct.

### **Timeout errors (H12, H13 on Render)**
- Increase `GUNICORN_TIMEOUT` to 180.
- Reduce `GUNICORN_THREADS` to 2 (less contention, faster inference).
- Check inference speed locally; if fast, the issue is likely network.

### **Out of Memory (OOM killed)**
- Reduce `GUNICORN_THREADS` to 2.
- Disable the optional leaf-detector model (`LEAF_DETECTOR_PATH` in app.py).
- Upgrade to paid tier (1 GB+ RAM).

### **Cold Start is Slow**
- **Expected**: First request after idle time takes 20–30s (model loading + inference).
- **Mitigation**: Use a service like Uptime Robot to ping `/health` every 5 minutes.
- **Better**: Upgrade to paid tier; more stable performance.

### **Logs are Unclear**
- In Render dashboard, view **Logs** tab.
- Look for `TensorFlow` or `Keras` warnings; check the last few lines.
- Enable Python logging: Set `FLASK_ENV=production` (already done).

---

## 📚 Additional Resources

- **Render Docs**: https://render.com/docs
- **Gunicorn Docs**: https://docs.gunicorn.org
- **TensorFlow Deployment**: https://www.tensorflow.org/guide/keras/export_savedmodel
- **Flask Deployment**: https://flask.palletsprojects.com/deployment/

---

## ✨ Next Steps

1. Commit and push all deployment files to GitHub:
   ```bash
   git add requirements.txt runtime.txt Procfile render.yaml .github/workflows/deploy_render.yml
   git commit -m "Add production deployment config (Render, Gunicorn, Python 3.10)"
   git push origin main
   ```

2. Deploy via Render:
   - Option A: Use the Render dashboard (easiest).
   - Option B: Push the repo; Render auto-detects `render.yaml`.

3. Test the live URL and monitor logs.

4. (Optional) Set up GitHub Actions auto-deploy by adding `RENDER_API_KEY` and `RENDER_SERVICE_ID` secrets.

---

**Good luck with your deployment! 🚀**
