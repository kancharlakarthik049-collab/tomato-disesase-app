FROM tensorflow/tensorflow:2.10.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

WORKDIR /app

# Install small system deps required by Pillow and common builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Upgrade pip, install wheels first, then requirements without cache
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project
COPY . /app

# Ensure uploads and debug dirs exist
RUN mkdir -p /app/static/uploads /app/static/uploads/debug && \
    chown -R root:root /app

EXPOSE ${PORT}

# Lightweight healthcheck for orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:${PORT}/health || exit 1

# Run with a small number of workers; keep exec form for PID 1
CMD ["sh", "-c", "gunicorn --workers 3 --bind 0.0.0.0:${PORT} app:app"]
