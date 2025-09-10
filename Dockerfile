FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Build wheels to avoid build deps in final image
RUN python -m pip install --upgrade pip \
  && pip wheel --wheel-dir /wheels -r requirements.txt

######################################################################
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GUNICORN_WORKER_CLASS=gevent \
    GUNICORN_WORKER_CONNECTIONS=1000

WORKDIR /app

# Runtime OS deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /usr/sbin/nologin appuser

# Install Python deps from prebuilt wheels
COPY requirements.txt ./
COPY --from=builder /wheels /wheels
RUN python -m pip install --upgrade pip \
  && pip install --no-index --find-links /wheels -r requirements.txt \
  && pip cache purge

# Copy application code
COPY . /app

# Ensure scripts are executable (if they exist)
RUN if [ -f /app/run-gunicorn.sh ]; then chmod +x /app/run-gunicorn.sh; fi

# Create writable dirs for Django collectstatic/media if using read-only root in orchestrators
RUN mkdir -p /app/staticfiles /app/media && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Healthcheck hits Django health endpoint
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -fsS http://localhost:8000/health/ || exit 1

CMD ["./run-gunicorn.sh"]


