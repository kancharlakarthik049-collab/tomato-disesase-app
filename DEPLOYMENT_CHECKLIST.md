# Deployment Checklist - Tomato Disease Identification

Complete this checklist before, during, and after deploying to Render.

---

## 📋 Pre-Deployment Checklist

### Local Testing
- [ ] Python environment activated (`.venv\Scripts\Activate.ps1` or `source venv/bin/activate`)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] App runs locally: `python app.py` → accessible at `http://localhost:5000/`
- [ ] `/health` endpoint responds: `curl http://localhost:5000/health`
- [ ] Model file exists: `models/tomato_model.h5` (~151 MB)
- [ ] Model loads without errors
- [ ] Can upload test image (JPG/PNG) and get prediction
- [ ] API endpoint works: `curl -X POST http://localhost:5000/api/predict -F "file=@test.jpg"`
- [ ] Error pages display correctly (test with invalid URL)
- [ ] Admin panel accessible: `http://localhost:5000/admin`
- [ ] No console errors during testing
- [ ] All Flask routes return correct status codes

### Code Quality
- [ ] No hardcoded secrets (passwords, API keys, URLs)
- [ ] All environment variables have defaults or are documented
- [ ] Code follows Python conventions (PEP 8)
- [ ] Error handling implemented for edge cases
- [ ] Graceful failure on model loading failure
- [ ] No debug print statements left in code
- [ ] Logging configured appropriately

### Project Files
- [ ] `requirements.txt` — all dependencies listed and pinned
- [ ] `runtime.txt` — Python version specified (3.10.13)
- [ ] `Procfile` — correct web process command
- [ ] `render.yaml` — Render infrastructure config present
- [ ] `.gitignore` — excludes `.env`, `__pycache__`, venv, uploads
- [ ] `.gitattributes` — Git LFS configured for `.h5` files
- [ ] `.env.example` — template with all variables documented
- [ ] `app.py` — production config (DEBUG=False, error handlers)
- [ ] `templates/`:
  - [ ] `index.html` — web UI present
  - [ ] `404.html` — custom error page
  - [ ] `500.html` — custom error page
  - [ ] `admin.html` — admin panel (optional)
  - [ ] `preview.html` — preview page (optional)
- [ ] `static/style.css` — CSS present

### Git Preparation
- [ ] Git repository initialized: `git init` or `.git/` exists
- [ ] Remote configured: `git remote -v` shows GitHub URL
- [ ] Git LFS initialized: `git lfs install`
- [ ] Model file tracked with LFS: `cat .gitattributes | grep h5`
- [ ] `.env` file NOT in repository (check `.gitignore`)
- [ ] All project files added: `git add .`
- [ ] Initial commit created with descriptive message
- [ ] No uncommitted changes: `git status` shows clean tree
- [ ] Repository pushed to GitHub: `git push origin main`
- [ ] GitHub Actions workflow file present: `.github/workflows/deploy_render.yml`

---

## 🔧 Deployment Configuration Checklist

### Render Account Setup
- [ ] Render account created (https://render.com)
- [ ] GitHub account connected to Render
- [ ] Repository authorized in GitHub OAuth

### Render Service Setup
- [ ] Service name set: `tomato-disease-detector`
- [ ] GitHub repository selected and connected
- [ ] Branch set to: `main`
- [ ] Environment detected: `Python 3`
- [ ] Build command configured: `pip install -r requirements.txt`
- [ ] Start command configured from `Procfile`
- [ ] Plan selected: `Free` (512 MB RAM)
- [ ] Region selected: `Oregon` (or closest)
- [ ] Health check path set: `/health`
- [ ] Auto-deploy on push enabled: `git push origin main` triggers deploy

### Environment Variables
- [ ] `FLASK_ENV=production` set in Render
- [ ] `GUNICORN_WORKERS=1` set (or left as default)
- [ ] `GUNICORN_THREADS=4` set (or left as default)
- [ ] `GUNICORN_TIMEOUT=120` set (or left as default)
- [ ] `MODEL_URL` left empty (model in Git LFS) OR set to external URL
- [ ] Any application-specific variables configured
- [ ] No secrets visible in rendered config file
- [ ] Environment variables match `.env.example`

---

## 🚀 Deployment Process Checklist

### Before Clicking "Create"
- [ ] Review all configuration one final time
- [ ] Service name is correct
- [ ] Repository is correct
- [ ] Build command is correct
- [ ] Start command is correct
- [ ] Health check endpoint configured
- [ ] Environment variables complete

### Creating Service
- [ ] Clicked "Create Web Service"
- [ ] Service creation started
- [ ] Monitoring deployment logs in real-time

### During Deployment
- [ ] Build phase completed successfully
- [ ] Dependencies installed (check for pip errors)
- [ ] Service started without errors
- [ ] Model file loaded successfully
- [ ] Health check passing
- [ ] No ERROR or CRITICAL level logs

### First Deployment (typically 2-3 minutes)
- [ ] Build completed
- [ ] Service running
- [ ] Public URL generated and assigned
- [ ] HTTPS certificate provisioned
- [ ] Service reports "Healthy"

---

## ✅ Post-Deployment Verification Checklist

### Live Service URL
- [ ] Service has public HTTPS URL: `https://<name>.onrender.com`
- [ ] URL is accessible from browser (green HTTPS lock visible)
- [ ] URL works with and without `/` suffix
- [ ] Service status shows "Active" in Render dashboard

### Endpoint Testing
- [ ] Health check returns 200: `curl https://<url>/health`
- [ ] Response indicates model loaded: `"model_loaded": true`
- [ ] Home page loads: `https://<url>/`
- [ ] Web UI displays correctly
- [ ] Mobile responsive (open in mobile browser or use dev tools)

### Functionality Testing
- [ ] Can upload test image via web UI
- [ ] Prediction returns without error
- [ ] Prediction format is correct
- [ ] File upload rejects invalid formats (non-image files)
- [ ] File upload rejects oversized files (>16MB)
- [ ] Admin panel accessible: `https://<url>/admin`
- [ ] API endpoint responds: `curl -X POST https://<url>/api/predict -F "file=@test.jpg"`

### Performance Testing
- [ ] First request completes (may take 30-60 sec: cold start)
- [ ] Subsequent requests complete in 2-5 seconds
- [ ] No timeout errors (504 Gateway Timeout)
- [ ] Memory usage stable (check logs)
- [ ] CPU usage reasonable

### Security Check
- [ ] HTTPS enabled (green lock in browser)
- [ ] No mixed content warnings
- [ ] Security headers present:
  - [ ] X-Frame-Options
  - [ ] X-Content-Type-Options
  - [ ] X-XSS-Protection
  - [ ] Strict-Transport-Security
- [ ] No debug information exposed in error pages
- [ ] No stack traces visible in errors

### Logging & Monitoring
- [ ] Render dashboard shows service as running
- [ ] Logs tab shows deployment and startup messages
- [ ] No ERROR or CRITICAL level errors
- [ ] Health check endpoint called regularly
- [ ] Request logs visible in logs panel

### Documentation
- [ ] Live URL noted and saved
- [ ] Deployment procedure documented
- [ ] Any configuration changes noted
- [ ] Troubleshooting notes saved
- [ ] Shared with team/stakeholders

---

## 🧪 Testing Endpoints

Use these curl commands to test (replace URL with your actual URL):

```bash
# Health check (essential)
curl https://<your-url>/health

# Home page
curl https://<your-url>/

# Admin panel
curl https://<your-url>/admin

# API prediction (with test image)
curl -X POST https://<your-url>/api/predict \
  -F "file=@path/to/leaf_image.jpg"

# Test invalid file
curl -X POST https://<your-url>/api/predict \
  -F "file=@test.txt"  # Should be rejected
```

---

## 🚨 Troubleshooting During Deployment

### Build Fails
- [ ] Check build logs for error message
- [ ] Verify `requirements.txt` has all dependencies
- [ ] Check `runtime.txt` for Python version compatibility
- [ ] Verify no syntax errors in `app.py`
- [ ] Ensure Git LFS is configured if using model

### Service Won't Start
- [ ] Check start command in `Procfile`
- [ ] Verify model file path is correct
- [ ] Check for port binding issues
- [ ] Review logs for permission errors
- [ ] Check available memory (512 MB limit on free tier)

### Model Not Loading
- [ ] Verify `models/tomato_model.h5` exists in repo
- [ ] If using external model, set `MODEL_URL` env var
- [ ] Check model file permissions
- [ ] Verify TensorFlow version compatibility
- [ ] Check available memory

### Timeouts/Slow Performance
- [ ] Increase `GUNICORN_TIMEOUT` to 180
- [ ] Reduce `GUNICORN_THREADS` to 2
- [ ] Check network latency
- [ ] Review model preprocessing time
- [ ] Consider model optimization/quantization

### Out of Memory
- [ ] Free tier has 512 MB total
- [ ] TensorFlow takes ~200 MB
- [ ] Reduce number of threads
- [ ] Disable optional features
- [ ] Upgrade to paid tier

---

## 📊 Performance Metrics to Monitor

### Expected Performance
- [ ] Cold start (after sleep): 30-60 seconds
- [ ] Warm start (subsequent requests): 2-5 seconds
- [ ] Model inference: 1-3 seconds
- [ ] Image preprocessing: <1 second
- [ ] Memory usage: ~300-400 MB
- [ ] CPU usage: <80% (during inference)

### Metrics to Track
- [ ] Health check response time
- [ ] Average request duration
- [ ] Error rate (should be <1%)
- [ ] Memory usage trend
- [ ] Number of active connections

---

## 🔐 Security Checklist

- [ ] No secrets in code repository
- [ ] `.env` file excluded from git
- [ ] HTTPS enabled (automatic on Render)
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] File upload validation implemented
- [ ] File size limits enforced
- [ ] No directory traversal vulnerabilities
- [ ] Error messages don't expose sensitive info

---

## 📈 Post-Launch Monitoring

### Week 1 (High Priority)
- [ ] Monitor for errors daily
- [ ] Check logs for unusual patterns
- [ ] Verify predictions are accurate
- [ ] Monitor performance metrics
- [ ] Respond to any user issues

### Week 2-4 (Regular)
- [ ] Weekly log review
- [ ] Verify health metrics stable
- [ ] Check user feedback
- [ ] Monitor uptime
- [ ] Plan any optimizations

### Ongoing (Monthly)
- [ ] Review performance trends
- [ ] Check for security updates
- [ ] Monitor costs (if using paid tier)
- [ ] Gather user feedback
- [ ] Plan improvements

---

## 🚀 If Redeploy is Needed

- [ ] Fix issue locally
- [ ] Test locally
- [ ] Commit changes: `git add . && git commit -m "Fix issue"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Render auto-redeploys on push
- [ ] Monitor logs until deployment completes
- [ ] Verify fix with testing

---

## ✨ After Deployment

### Share Your App
- [ ] Get public URL: `https://<service-name>.onrender.com`
- [ ] Share URL with team/users
- [ ] Add to portfolio or resume
- [ ] Document in project README
- [ ] Share on social media (optional)

### Continuous Improvement
- [ ] Collect user feedback
- [ ] Monitor error logs
- [ ] Track usage statistics
- [ ] Plan feature improvements
- [ ] Optimize based on performance data

---

## 📞 Support Resources

| Resource | Link | Use Case |
|----------|------|----------|
| **Render Docs** | https://render.com/docs | Render-specific issues |
| **Flask Docs** | https://flask.palletsprojects.com | Flask questions |
| **TensorFlow Docs** | https://tensorflow.org | ML model issues |
| **Gunicorn Docs** | https://docs.gunicorn.org | Server issues |
| **GitHub Issues** | Create issue in repo | Project-specific bugs |

---

## 💡 Common Mistakes to Avoid

- ❌ Hardcoding database URLs or API keys
- ❌ Using `debug=True` in production
- ❌ Forgetting to Pin dependency versions
- ❌ Missing error handling for model loading
- ❌ Committing `.env` file to git
- ❌ Not testing locally before deploying
- ❌ Ignoring log messages during deployment
- ❌ Setting memory-intensive timeouts
- ❌ Multiple Gunicorn workers on free tier
- ❌ Deploying without health check endpoint

---

## 🎯 Success Criteria

Your deployment is successful when:

✅ Service status is "Active"  
✅ Health endpoint returns 200 with `"model_loaded": true`  
✅ Web UI is accessible and responsive  
✅ Can upload images and get predictions  
✅ No error logs (except normal 404s for non-existent routes)  
✅ Performance is acceptable (<5 sec per prediction)  
✅ HTTPS enabled (green lock in browser)  
✅ All endpoints documented and tested  

---

**Last Updated**: February 21, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
