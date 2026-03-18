# Large Model File Handling Guide

**Model File Size**: ~151 MB  
**Status**: Configured for Git LFS (Git Large File Storage)  
**Date**: February 21, 2026

---

## 📊 Problem Statement

The `tomato_model.h5` file (InceptionV3 trained model) is **~151 MB**, which exceeds:
- GitHub's recommended max file size: **100 MB**
- Good practice for repository size: **50 MB**

Committing large files to Git can:
- Slow down cloning and pulling
- Increase repository size unnecessarily
- Hit GitHub's limits on free tier

---

## ✅ Solution Implemented: Git LFS (Option A)

### What is Git LFS?

**Git LFS (Large File Storage)** is a Git extension that:
- Stores large files on a separate LFS server (not in your Git history)
- Tracks file references in `.gitattributes` instead of the actual files
- Keeps your repository small and fast
- Works seamlessly with GitHub (automatic support)

### Configuration: `.gitattributes`

File: [.gitattributes](.gitattributes)

```gitattributes
# Keras/TensorFlow models
models/*.h5 filter=lfs diff=lfs merge=lfs -text
*.h5 filter=lfs diff=lfs merge=lfs -text

# TensorFlow Lite models
models/*.tflite filter=lfs diff=lfs merge=lfs -text
*.tflite filter=lfs diff=lfs merge=lfs -text

# ONNX models
*.onnx filter=lfs diff=lfs merge=lfs -text

# PyTorch models
*.pth filter=lfs diff=lfs merge=lfs -text

# Pickle files
*.pkl filter=lfs diff=lfs merge=lfs -text
```

---

## 🚀 How to Use Git LFS

### Step 1: Install Git LFS

**Windows**:
```powershell
# Using Chocolatey
choco install git-lfs

# Or download from: https://git-lfs.github.com/
# Run installer and follow prompts
```

**macOS**:
```bash
brew install git-lfs
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install git-lfs
```

### Step 2: Initialize Git LFS in Your Repository

Run this once per repository:

```bash
git lfs install
```

This sets up Git LFS hooks in your `.git` directory.

### Step 3: Track Large Files

Files are already configured in `.gitattributes`:

```bash
# Files matching patterns in .gitattributes are auto-tracked
# No additional action needed for *.h5 files

# (Optional) Manually track other large files:
git lfs track "path/to/large/file.ext"
```

### Step 4: Commit & Push as Normal

```bash
git add models/tomato_model.h5
git add .gitattributes
git commit -m "Add tomato_model.h5 (tracked with Git LFS)"
git push origin main
```

Git LFS automatically handles the upload to the LFS server.

### Step 5: Clone Repository with LFS Files

```bash
# Clone normally - Git LFS files are automatically downloaded
git clone https://github.com/username/tomato-diseace-identification.git

# If you cloned before LFS was set up:
git lfs pull
```

---

## ✨ Benefits of Git LFS Implementation

| Benefit | Details |
|---------|---------|
| **Small Repository** | Git history stays small (no model file copies for each commit) |
| **Fast Cloning** | Download only the latest model version, not history |
| **GitHub Friendly** | Free tier supports LFS (1 GB storage + 1 GB bandwidth/month) |
| **Transparent** | Works with standard Git commands; no workflow changes |
| **Versioning** | Can still track model versions via Git tags |

---

## 🔄 Alternative Option B: Model Externalization (For Render Deployment)

If you prefer **not to use Git LFS** or want to minimize repository size, externalize the model file:

### Setup:

1. **Remove model from Git**:
   ```bash
   git rm --cached models/tomato_model.h5
   echo "models/tomato_model.h5" >> .gitignore
   git add .gitignore
   git commit -m "Remove model file from git (will be downloaded at runtime)"
   ```

2. **Upload model to cloud storage** (free options):
   - **Google Drive**: Get shareable public link
   - **AWS S3**: Free tier 5 GB (requires account)
   - **Azure Blob Storage**: Free tier 5 GB
   - **Hugging Face**: Free model hosting (recommended!)

3. **Set MODEL_URL environment variable** in Render:
   ```bash
   MODEL_URL=https://your-storage-bucket.s3.amazonaws.com/tomato_model.h5
   ```

4. **App automatically downloads at startup**:
   The app already has this logic (see [app.py](app.py#L400-L410)):
   ```python
   if not os.path.exists(MODEL_PATH) and model_url:
       resp = requests.get(model_url, stream=True, timeout=60)
       with open(MODEL_PATH, 'wb') as f:
           for chunk in resp.iter_content(chunk_size=8192):
               f.write(chunk)
   ```

### Pros & Cons:

| Aspect | Pros | Cons |
|--------|------|------|
| **Repo Size** | ✅ Minimal (no model) | - |
| **Cold Start** | - | ⚠️ First request: 30-60s (model download + load) |
| **Reliability** | ✅ Independent from Git | ⚠️ Depends on external storage availability |
| **Cost** | ✅ Free (within tier limits) | ⚠️ Bandwidth limits (100 GB/month on S3) |

---

## 📋 Current Configuration Summary

### Git LFS Status

| Item | Status |
|------|--------|
| `.gitattributes` | ✅ Configured |
| `models/tomato_model.h5` | ✅ Ready for LFS |
| Git LFS installed | ⚠️ Requires manual installation |

### Setup Checklist

- [ ] Install Git LFS on your machine (`git lfs install`)
- [ ] Run `git lfs install` in repo directory
- [ ] Push model file with Git LFS (`git push`)

### Render Deployment Impact

**With Git LFS**:
- Model file is cloned during Render build
- No additional env vars needed
- Deploy time: Normal (~1-2 min)

**With Model Externalization**:
- Model is downloaded at runtime
- Requires `MODEL_URL` env var in Render
- First request takes longer (~5-10 sec additional)

---

## 🔧 Recommended Approach for This Project

### **Use Git LFS** (Current Setup) ✅

**Reasons**:
1. Model is essential to the app (not optional)
2. Simple setup; transparent workflow
3. GitHub free tier supports LFS well
4. No extra runtime dependency on external storage
5. Faster app startup (no download delay)

**Steps to finalize**:
```bash
# 1. Install Git LFS if not already done
git lfs install

# 2. Ensure .gitattributes is tracked
git add .gitattributes
git commit -m "Configure Git LFS for model files"

# 3. Push to GitHub
git push origin main

# 4. GitHub will detect LFS files and store them appropriately
```

---

## 📚 Additional Resources

- **Git LFS Docs**: https://git-lfs.github.com/
- **GitHub LFS Support**: https://docs.github.com/en/repositories/working-with-files/managing-large-files
- **Hugging Face Models**: https://huggingface.co/models (free model hosting)
- **AWS S3 Free Tier**: https://aws.amazon.com/s3/pricing/
- **Google Drive API**: https://developers.google.com/drive

---

## ⚠️ Important Notes

### If You Haven't Pushed the Model Yet

1. Ensure Git LFS is installed: `git lfs install`
2. Push normally: `git add models/tomato_model.h5 && git commit && git push`
3. GitHub will handle LFS storage automatically

### If Model is Already in Git History

Git LFS can't retroactively remove files from history (storage-intensive operation). Options:

1. **Keep as is** (repository is larger, but functional)
2. **Use BFG Repo Cleaner** (advanced; rewrites history)
3. **Start fresh** with a new repository using Git LFS from the beginning

For this project, since the repo is fresh with Render deployment, simply:
```bash
# Ensure Git LFS is configured before first push
git lfs install
git add .
git commit -m "Add project files with Git LFS for model"
git push origin main
```

---

## ✅ Implementation Status

| Task | Status | Details |
|------|--------|---------|
| `.gitattributes` created | ✅ Complete | Tracks `.h5`, `.tflite`, `.onnx`, `.pth`, `.pkl` |
| Git LFS patterns | ✅ Complete | Configured for model files |
| Documentation | ✅ Complete | This guide |
| App support | ✅ Complete | Already handles external models via `MODEL_URL` |
| Render integration | ✅ Complete | `render.yaml` works with Git LFS |

**Next Step**: Install Git LFS and push to GitHub.

---

## 🎯 For Render Deployment

Once files are pushed to GitHub with Git LFS:

1. Render clones your repo automatically
2. Git LFS files are downloaded during build
3. `pip install -r requirements.txt` runs
4. App starts with `gunicorn` — model is already in place
5. No additional configuration needed!

**Result**: Fast, reliable deployment with all assets in place. 🚀
