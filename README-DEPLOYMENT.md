# Deployment Guide - Tomato Disease Identification App

**Target Platform**: Render (Free Tier)  
**Model**: InceptionV3 (TensorFlow)  
**Framework**: Flask + Gunicorn  
**Live URL**: `https://<your-service-name>.onrender.com`

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ **GitHub Account**: https://github.com (free)
- ✅ **Render Account**: https://render.com (free, sign in with GitHub)
- ✅ **Git Installed**: https://git-scm.com/
- ✅ **Project on GitHub**: Repository already created (you have this)

---

## 🚀 Quick Deployment Steps

### **Step 1: Test Local Environment**

Verify everything works before deploying:

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1     # Windows PowerShell
# or
source .venv/bin/activate      # Linux/macOS

# Install dependencies (if not already done)
pip install -r requirements.txt

# Run app locally (test mode)
python app.py
# Visit http://localhost:5000/

# Test prediction endpoint
curl http://localhost:5000/health
# Expected: {"status":"ok"}

# Stop the app (Ctrl+C)
```

### **Step 2: Prepare Git Repository**

Ensure all files are committed:

```bash
# Check Git status
git status

# If using Git LFS for model file
git lfs install
bash setup_git_lfs.sh

# Stage all files
git add .

# Commit changes
git commit -m "Production deployment ready: Flask config, Gunicorn, error handlers, deployment guides"

# Push to GitHub
git push origin main
```

### **Step 3: Create Render Web Service**

1. **Go to Render Dashboard**:
   - Visit https://render.com/dashboard
   - Sign in with your GitHub account

2. **Create New Web Service**:
   - Click **"New +"** button (top-right)
   - Select **"Web Service"**

3. **Connect GitHub Repository**:
   - Select your GitHub account
   - Search for `tomato-diseace-identification`
   - Click **"Connect"**

4. **Configure Service**:
   
   | Setting | Value |
   |---------|-------|
   | **Name** | `tomato-disease-detector` |
   | **Environment** | `Python 3` (auto-detected) |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | Use from `Procfile` or enter manually |
   | **Plan** | `Free` (512 MB RAM) |
   | **Region** | `Oregon` (default, or closest to you) |

5. **Set Environment Variables** (if needed):
   - Click **"Environment"** tab
   - Add variables from `.env.example`:
     - `FLASK_ENV=production`
     - `GUNICORN_WORKERS=1`
     - `GUNICORN_THREADS=4`
     - `GUNICORN_TIMEOUT=120`
   - Leave `MODEL_URL` empty (model is in Git LFS)

6. **Deploy**:
   - Click **"Create Web Service"**
   - Wait 2-3 minutes for deployment
   - Check deployment progress in "Logs" tab

### **Step 4: Verify Deployment**

Once deployment completes:

```bash
# Test health endpoint
curl https://<your-service-name>.onrender.com/health
# Expected response:
# {"status":"ok","model_loaded":true,...}

# Test web UI
# Visit: https://<your-service-name>.onrender.com/

# Test API endpoint
curl -X POST https://<your-service-name>.onrender.com/api/predict \
  -F "file=@leaf_image.jpg"
```

### **Step 5: Share Your App**

Your app is now live! Share the URL:
```
https://<your-service-name>.onrender.com/
```

---

## 🔧 Automated Deployment (Alternative)

If you prefer automated setup:

```bash
# Run deployment script (validates + commits + pushes)
bash deploy.sh

# Follow prompts to confirm
# Script will:
# ✅ Validate all required files
# ✅ Check Git repository
# ✅ Stage deployment files
# ✅ Create commit
# ✅ Push to GitHub
# ✅ Show next steps
```

---

## ⚙️ Environment Variables

Reference of all configurable environment variables (most have sensible defaults):

### **Essential**
- `FLASK_ENV=production` — Disables debug mode
- `PORT` — Set by Render (usually 80 or dynamic)

### **Gunicorn Server**
- `GUNICORN_WORKERS=1` — Keep at 1 for free tier
- `GUNICORN_THREADS=4` — Concurrent request handling
- `GUNICORN_TIMEOUT=120` — Timeout for slow requests

### **Model Loading**
- `MODEL_URL=` — Leave empty (model in Git LFS)
- `MODEL_PATH=models/tomato_model.h5` — Model file location

### **Optional Tuning**
- `GREEN_H_MIN=25`, `GREEN_H_MAX=100` — Leaf detection
- `S_MIN=40`, `V_MIN=40` — Color space thresholds
- `CONF_THRESH=0.4` — Confidence threshold

**Full reference**: See [.env.example](.env.example)

---

## 🐛 Troubleshooting

### **Build Fails ("build failed")**

**Error Message**: "Build failed - see logs"

**Solution**:
1. Go to Render dashboard → Your service → Logs
2. Look for error message in last 50 lines
3. Common issues:
   - Missing dependency in `requirements.txt`
   - Syntax error in Python files
   - Incorrect Python version in `runtime.txt`

**Fix**:
```bash
# Fix issue locally
# ...update code...

# Re-deploy
git add .
git commit -m "Fix build error"
git push origin main
# Render auto-redeploys
```

---

### **"Service failed to start" or "502 Bad Gateway"**

**Error**: App crashes after build

**Solution**:
1. Check logs for error messages
2. Common causes:
   - Model file not found
   - Memory exhausted (TensorFlow is large)
   - Syntax error in `app.py`

**Fix**:
```bash
# Test locally first
python app.py  # Should run without errors

# Check model file exists
ls -la models/tomato_model.h5  # Should be ~151 MB

# If using external model, set MODEL_URL
# In Render dashboard → Environment → Add MODEL_URL=<file_id>
```

---

### **Model Loading Timeout ("504 Gateway Timeout")**

**Error**: First request takes >120 seconds

**Causes**:
- Model file is large (151 MB)
- Inference is slow (normal for InceptionV3)
- Network speed is slow

**Solution**:
```bash
# Increase timeout in environment variables
GUNICORN_TIMEOUT=180  # 3 minutes

# Or reduce threads
GUNICORN_THREADS=2    # Less contention
```

---

### **Out of Memory ("OOM killer")**

**Error**: App crashes with memory error

**Causes**:
- Free tier has only 512 MB RAM
- TensorFlow model uses ~200 MB
- Multiple threads each loading model

**Solutions** (in order of ease):
1. Reduce threads:
   ```bash
   GUNICORN_THREADS=2  # was 4
   ```

2. Upgrade to paid tier:
   - Render paid tier has 1+ GB RAM
   - Estimated cost: $7/month

3. Use TensorFlow Lite (smaller model):
   - Quantize model to ~30 MB
   - Trade-off: Slightly less accuracy

---

### **"Model not found" Error**

**Error**: App says model file missing

**Solution**:
- If using Git LFS:
  ```bash
  # Ensure .gitattributes has *.h5
  cat .gitattributes | grep "h5"
  
  # Re-push if needed
  git push origin main --force
  ```

- If using external storage (MODEL_URL):
  ```bash
  # Set MODEL_URL in Render environment variables
  # Navigate to: Settings → Environment Variables → Add MODEL_URL=<file_id>
  ```

---

### **Slow Predictions ("takes 30+ seconds")**

**Causes**:
- First request after app sleeps (30-60 sec cold start)
- Large model (InceptionV3 is ~151 MB)
- Image preprocessing
- Inference time (normal: 1-5 seconds)

**Expected performance**:
- Cold start (after idle): 30-60 seconds
- Warm requests: 2-5 seconds

**To reduce cold starts**:
- Upgrade to paid tier (keeps instance warm)
- Use keepalive service (ping every 5 min)
- Optimize frontend with loading indicator

---

## 📊 Expected Performance

### **Free Tier**
- Memory: 512 MB
- CPU: Shared 0.5 vCPU
- Cold start: 30-60 seconds (first request after idle)
- Warm requests: 2-5 seconds per prediction
- Uptime: Sleeps after 15 min inactivity

### **Paid Tier** (if you upgrade)
- Memory: 1+ GB (more headroom)
- CPU: Better performance
- Faster inference
- No sleep periods
- Cost: ~$7-20/month (depending on selection)

---

## 🔐 Security Notes

### **Already Implemented** ✅
- ✅ HTTPS enabled (automatic on Render)
- ✅ Secret data not in code (environment variables only)
- ✅ File upload validation (only JPG/PNG)
- ✅ Model loading error handling
- ✅ CORS restricted (can be tightened)
- ✅ Security headers (X-Frame-Options, X-Content-Type-Options)

### **Recommendations**
- If sharing publicly, add authentication to `/admin` panel
- Use environment variables for all usernames/passwords
- Monitor logs for suspicious activity
- Consider adding rate limiting for API endpoints

---

## 📚 Additional Resources

| Resource | Link | Purpose |
|----------|------|---------|
| **Render Docs** | https://render.com/docs | Official documentation |
| **Flask Docs** | https://flask.palletsprojects.com | Flask framework |
| **Gunicorn Docs** | https://docs.gunicorn.org | WSGI server |
| **TensorFlow Docs** | https://tensorflow.org | Machine learning |
| **Git LFS** | https://git-lfs.github.com | Large file handling |

---

## ✅ Post-Deployment Checklist

After your app goes live:

- [ ] App loads without errors
- [ ] Health check endpoint responds
- [ ] Web UI displays correctly
- [ ] Can upload image files
- [ ] Model makes predictions correctly
- [ ] Error pages display properly
- [ ] Mobile responsive (test on phone)
- [ ] HTTPS working (green lock in browser)
- [ ] Performance is acceptable
- [ ] Logs show no errors

---

## 🎉 Success!

Your Flask Tomato Disease Identification app is now live and accessible to the world!

### **What's Next?**

1. **Share the URL**: Send to colleagues/friends
2. **Monitor**: Check Render logs occasionally for errors
3. **Improve**: Collect user feedback and iterate
4. **Scale**: If needed, upgrade to paid tier for better performance

---

## 💬 Questions?

Refer to these guides for more information:
- [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) — Comprehensive deployment guide
- [.env.example](.env.example) — All environment variables
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) — Complete pre/post deployment checklist

**Questions about your specific error? Check the Troubleshooting section above or reference the detailed guides.**

---

**Happy deploying! 🚀**
