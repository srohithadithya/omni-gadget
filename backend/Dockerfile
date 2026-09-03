# ═══════════════════════════════════════════════════════════════════════════════
# Dockerfile — AIDE-OS Backend (FastAPI + psycopg2)
# ═══════════════════════════════════════════════════════════════════════════════
# Multi-stage build for smaller image (~180 MB vs ~900 MB naive)
#
# Build:  docker build -t aide-os-api .
# Run:    docker run -p 8000:8000 -e DATABASE_URL=... -e REDIS_URL=... aide-os-api
# ═══════════════════════════════════════════════════════════════════════════════

# ── Stage 1: Build dependencies ────────────────────────────────────────────────
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Runtime deps: only libpq (no compiler needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Copy pre-built Python packages from builder
COPY --from=builder /install /usr/local

# Non-root user for security
RUN groupadd -r aide && useradd -r -g aide -d /app -s /sbin/nologin aide

WORKDIR /app

# Copy application code
COPY app/ ./app/

# Ensure python path includes /app so `app.main` resolves
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Port will be set by Render via $PORT env var
EXPOSE 8000

# Switch to non-root user
USER aide

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
