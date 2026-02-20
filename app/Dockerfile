# ==============================================================
# MULTI-STAGE DOCKERFILE
# ==============================================================
# WHY MULTI-STAGE?
# Stage 1 (test): Installs everything, runs tests — large image (~900MB)
# Stage 2 (production): Only copies what's needed — small image (~150MB)
#
# This means:
# - Tests run during every build (if tests fail, image isn't created)
# - Production image is small and secure (no test tools, no build tools)
# - Faster deployments (smaller image = faster pull from registry)
# ==============================================================


# ------ STAGE 1: TEST ------
# This stage installs all dependencies and runs tests.
# If tests fail, the build stops here and no image is produced.

FROM python:3.11-slim AS test

# Set working directory inside the container
WORKDIR /app

# Copy requirements FIRST (Docker layer caching optimisation)
# WHY? Docker caches each layer. If requirements.txt hasn't changed,
# Docker reuses the cached layer and skips pip install (saves minutes).
# If we copied ALL files first, any code change would invalidate this cache.
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# NOW copy the application code
COPY . .

# Run tests — if any test fails, the build fails here
RUN python -m pytest tests/ -v --tb=short


# ------ STAGE 2: PRODUCTION ------
# Fresh, clean image with only what's needed to run the app.
# Nothing from Stage 1 carries over unless explicitly copied.

FROM python:3.11-slim AS production

# Metadata labels (good practice — shows up in docker inspect)
LABEL maintainer="Rabaanee Ahmed"
LABEL description="Deployment Tracker API"
LABEL version="1.0.0"

WORKDIR /app

# SECURITY: Create a non-root user
# WHY? If an attacker exploits the app, they get non-root access.
# This is a basic but important security practice that interviewers
# will specifically ask about.
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install only production dependencies (no pytest etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code only (no tests, no venv, no git files)
COPY app.py .

# SECURITY: Switch to non-root user
USER appuser

# Document which port the app uses
# NOTE: EXPOSE doesn't actually open the port — it's documentation.
# The actual port mapping happens when you run the container or in K8s.
EXPOSE 5000

# HEALTHCHECK: Docker will periodically check if the app is healthy
# This is different from Kubernetes probes but shows the same thinking
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# CMD vs ENTRYPOINT:
# CMD = default command (can be overridden)
# We use gunicorn (production WSGI server) instead of Flask's dev server
# --workers 2: handles concurrent requests (would scale this in production)
# --bind 0.0.0.0:5000: listen on all interfaces (required in containers)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]