# Eralove API — Production Dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# ── 1. Build Stage ──────────────────────────────────────
FROM base AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── 2. Production Runner Stage ──────────────────────────
FROM base AS runner

# Install Postgres runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy built python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend application files
COPY apps/api/src ./src
COPY apps/api/migrations ./migrations
COPY apps/api/alembic.ini ./alembic.ini

EXPOSE 8000

# Run Uvicorn production server
CMD ["uvicorn", "presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
