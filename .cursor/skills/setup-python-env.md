---
name: setup-python-env
description: Setup Python development environment — virtual env, dependencies, Docker, and dev server
---

# Setup Python Development Environment

## 1. Initial Setup

### Create Virtual Environment
```bash
cd apps/api
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
# or with uv (faster)
uv pip install -r requirements.txt
```

### Install Dev Dependencies
```bash
pip install -r requirements-dev.txt
# Includes: pytest, pytest-asyncio, ruff, mypy, httpx, factory-boy
```

## 2. Docker Development Environment

### Start All Services
```bash
# From project root
docker compose up -d

# Services:
# - postgres: PostgreSQL 16 on port 5432
# - redis: Redis 7 on port 6379
# - minio: S3-compatible storage on port 9000 (dev only)
```

### Docker Compose Configuration
```yaml
# infra/docker-compose.dev.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: eralove
      POSTGRES_USER: eralove
      POSTGRES_PASSWORD: eralove_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  minio_data:
```

## 3. Environment Variables

```bash
# apps/api/.env
# Database
DATABASE_URL=postgresql+asyncpg://eralove:eralove_dev@localhost:5432/eralove

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS S3 (MinIO for dev)
AWS_S3_BUCKET=eralove-media
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:9000

# Claude AI
CLAUDE_API_KEY=sk-ant-xxx

# App
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000"]
```

## 4. Database Setup

```bash
# Run migrations
cd apps/api && alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"

# Rollback last migration
alembic downgrade -1

# Show current migration
alembic current

# Show migration history
alembic history
```

## 5. Start Development Server

```bash
# FastAPI dev server with auto-reload
cd apps/api && uvicorn src.presentation.main:app --reload --host 0.0.0.0 --port 8000

# With Socket.IO (use socket_app instead)
cd apps/api && uvicorn src.presentation.main:socket_app --reload --host 0.0.0.0 --port 8000

# Celery worker (separate terminal)
cd apps/api && celery -A src.infrastructure.celery.config worker --loglevel=info

# Celery beat (separate terminal)
cd apps/api && celery -A src.infrastructure.celery.config beat --loglevel=info

# Flower monitoring (optional)
cd apps/api && celery -A src.infrastructure.celery.config flower --port=5555
```

## 6. Code Quality

```bash
# Lint
cd apps/api && ruff check src/

# Format
cd apps/api && ruff format src/

# Type check
cd apps/api && mypy src/

# Run tests
cd apps/api && pytest tests/ -v

# Run with coverage
cd apps/api && pytest --cov=src --cov-report=html
```

## 7. Seed Data (Development)

```bash
# Run seed script
cd apps/api && python scripts/seed.py

# Creates:
# - 2 test users (test@example.com, partner@example.com)
# - 1 couple
# - Sample events, photos, messages
# - Daily quiz questions
```

## Common Issues

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Check `.venv` is activated and deps installed |
| Database connection refused | Run `docker compose up -d postgres` |
| Redis connection refused | Run `docker compose up -d redis` |
| Alembic migration error | Check `alembic.ini` has correct `sqlalchemy.url` |
| Port 8000 in use | Kill process: `lsof -i :8000` or change port |
| Celery not finding tasks | Check task imports in `celery_app.autodiscover_tasks()` |
