This repo includes a Dockerfile for producing a production-ready image of the Tomato Disease app.

Quick build and run (local):

1. Build the image (from repo root):

```powershell
# build the image
docker build -t tomato-app:latest .

# run the container and map port 5000
docker run --rm -p 5000:5000 --name tomato-app tomato-app:latest
```

2. If you want to include your trained model file in the image, place `tomato_model.h5` into the `models/` directory before building. By default `models/` is excluded from the build context to avoid accidentally shipping large files; to include it, remove `models/` from `.dockerignore` (see instructions below).

3. Healthcheck endpoint: `GET /health`.

Notes:

Docker Compose (development)

A `docker-compose.yml` is provided to make local development easier. It mounts your local `models/` and `static/uploads/` folders into the container so you can iterate without rebuilding the image.

Commands:

```powershell
# build image and start service
docker-compose up --build

# stop and remove containers
docker-compose down
```

Windows Docker Desktop install notes

1. Install Docker Desktop for Windows: https://www.docker.com/products/docker-desktop
2. Enable WSL2 integration (recommended) during installation and restart your machine.
3. Open PowerShell and verify:

```powershell
docker --version
docker-compose --version
```

If `docker` is not recognized, make sure Docker Desktop is running and your PATH is updated.

Security note

The compose file mounts `models/` read-only into the container by default. If you need to include the model file in the image for CI/CD, remove `models/` from `.dockerignore` or provide a model-download step in your CI pipeline.

Include model in image (optional)

To bake `tomato_model.h5` into the Docker image do the following from the repo root:

```powershell
# ensure model is present locally
mkdir .\models -ErrorAction SilentlyContinue
Copy-Item C:\path\to\tomato_model.h5 .\models\

# remove models/ from .dockerignore so it is sent to the Docker daemon
# (you can also edit .dockerignore manually and comment out the `models/` line)

# build the image (model will be included)
docker build -t tomato-app:latest .
```

Notes:
- Including the model will increase image size. For CI/CD, consider uploading the model to a private storage (S3, GCS) and downloading it at build time or runtime instead of baking it into the image.
- If you prefer to keep the model out of the repo but still want images with the model, implement a build pipeline that injects the model as a build artifact.

CI / GitHub Actions

This repository includes a GitHub Actions workflow that builds and pushes the Docker image to Docker Hub on pushes to `main`.

Location: `.github/workflows/docker-publish.yml`

Required repository secrets (set these in GitHub Settings → Secrets):
- `DOCKERHUB_USERNAME` — your Docker Hub username
- `DOCKERHUB_TOKEN` — a Docker Hub access token or password

Optional secrets for model download at build time:
- `MODEL_URL` — URL where `tomato_model.h5` can be downloaded during the build
- `MODEL_TOKEN` — optional token used as a Bearer token in the `Authorization` header when downloading the model

The workflow will tag the pushed image as `yourdockerhubuser/tomato-app:latest`. You can edit the workflow to add additional tags (commit SHA, release tag, etc.).

By default the workflow now also tags the image with the commit SHA (e.g. `yourdockerhubuser/tomato-app:<sha>`). If you push a Git tag or use releases you may want to add a release tag in the workflow as well.

New tags pushed by the workflow:
- `latest` — the latest built image
- full commit SHA — e.g. `yourdockerhubuser/tomato-app:0123456789abcdef...`
- short SHA (7 chars) — e.g. `yourdockerhubuser/tomato-app:0123456`
- branch name — e.g. `yourdockerhubuser/tomato-app:main`

The workflow can also be triggered manually from the Actions tab (`workflow_dispatch`).

To enable automatic image pushes:
1. Create the above secrets in the GitHub repo.
2. Ensure the `models/` directory contains `tomato_model.h5` before pushing (or modify the workflow to fetch the model at build time).
3. Push to `main` and watch the Actions tab for the build logs.
