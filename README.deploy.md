Deploy (Docker)
---------------

Build and run the app in a portable container. The image does not include large model files by default — provide `MODEL_URL` or mount a local `models` directory.

Quick start (Linux/macOS):

```bash
./scripts/build_and_run.sh tomato-app:latest https://example.com/tomato_model.h5
```

Quick start (Windows PowerShell):

```powershell
.\scripts\build_and_run.ps1 -ImageName 'tomato-app:latest' -ModelUrl 'https://example.com/tomato_model.h5'
```

Notes:
- To mount a local model file instead of downloading, run the container with `-v $(pwd)/models:/app/models` and omit `MODEL_URL`.
- The app listens on port `5000` inside the container; the scripts map it to host `5000`.
- If you prefer to deploy to a cloud container service (Cloud Run, ECS, Azure App Service), build the same image and push to your container registry.

Environment variables supported:
- `PORT` — port that Gunicorn will bind to (default `5000`)
- `MODEL_URL` — an HTTP(S) URL the container will try to download at startup into `models/tomato_model.h5` if no model exists

All-in-one image (model baked into the image)
-------------------------------------------

If you'd like a single image that already contains the trained model (so it can "run anywhere" without runtime downloads), use `Dockerfile.allinone`. You can either provide a URL to download the model during image build, or place `models/tomato_model.h5` in the repository and build.

Build with a model URL (downloads during build):

```bash
./scripts/build_all_in_one.sh tomato-app:allinone https://example.com/tomato_model.h5
```

Or with PowerShell:

```powershell
.\scripts\build_all_in_one.ps1 -ImageName 'tomato-app:allinone' -ModelUrl 'https://example.com/tomato_model.h5'
```

If you already have `models/tomato_model.h5` locally and prefer to include it from the build context, either remove `models/` from `.dockerignore` temporarily or copy it into the build context and run:

```bash
docker build -f Dockerfile.allinone -t tomato-app:allinone .
```

Run the all-in-one image locally:

```bash
docker run --rm -p 5000:5000 tomato-app:allinone
```

CI / GitHub Actions
-------------------

This repo includes a workflow at `.github/workflows/ci-cd.yml` that:
- Builds `Dockerfile.allinone` and pushes images to GitHub Container Registry (`ghcr.io/<owner>/tomato-app`).
- Optionally deploys to Google Cloud Run when the following repository secrets are configured:
	- `MODEL_URL` (optional): HTTP(S) URL to download the model during image build if not present in the repo.
	- `GCP_SA_KEY` (optional): JSON service account key contents used to authenticate to GCP (set as a secret).
	- `GCP_PROJECT` (required for Cloud Run deploy): your GCP project id.
	- `GCP_REGION` (optional): region for Cloud Run (defaults to `us-central1`).

Secrets setup notes:
- To publish to GHCR, the workflow uses `GITHUB_TOKEN` automatically; no additional secret is required for pushing to the same org/user account.
- To enable Cloud Run deployment, create a service account with `roles/run.admin` and `roles/storage.admin` (for image access), download JSON, and store it as the `GCP_SA_KEY` repository secret.

Docker Hub support
------------------

If you prefer Docker Hub instead of GHCR, the workflow can push to Docker Hub when you add the following repository secrets:

- `DOCKERHUB_USERNAME` — your Docker Hub username
- `DOCKERHUB_PASSWORD` — Docker Hub password or access token

When present, the CI will build `Dockerfile.allinone` and push `DOCKERHUB_USERNAME/tomato-app:latest` to Docker Hub.

Health check
------------

When Cloud Run deploy is enabled, the workflow performs a health check against the deployed service using the `/health` endpoint. If the check fails, the workflow will fail so you can investigate logs.

Manual Cloud Run deploy helper
------------------------------

A helper script `deploy.sh` is provided to deploy an image manually with `gcloud`:

```bash
./deploy.sh ghcr.io/ORG/tomato-app:latest YOUR_GCP_PROJECT us-central1 tomato-app
```

Make sure you have run `gcloud auth login` or `gcloud auth activate-service-account --key-file=KEY.json` before using the script.


