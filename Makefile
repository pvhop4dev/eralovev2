# Eralove — Developer Automation Menu
# Compatible with both Windows (cmd/powershell) and Unix (macOS/Linux/Git Bash)

COMPOSE = docker compose
INFRA_COMPOSE_FILE = infra/docker-compose.yml
PROD_COMPOSE_FILE = deploy/docker-compose.prod.yml

# ── OS-specific execution configurations ─────────────────────────────────────
ifeq ($(OS),Windows_NT)
    SHELL = cmd.exe
    PYTHON = apps\api\.venv\Scripts\python.exe
    PIP = apps\api\.venv\Scripts\pip.exe
    ALEMBIC = apps\api\.venv\Scripts\alembic.exe
    PYTEST = apps\api\.venv\Scripts\pytest.exe
    RUFF = apps\api\.venv\Scripts\ruff.exe
    COPY_ENV = if not exist .env copy .env.example .env
    CREATE_VENV = if not exist apps\api\.venv python -m venv apps\api\.venv
    CLEAN_CMD = rmdir /s /q apps\web\.next node_modules apps\api\.pytest_cache 2>nul || ver >nul
    RUN_MIGRATE = cd apps\api && .venv\Scripts\alembic.exe upgrade head
    RUN_MIGRATE_CREATE = cd apps\api && .venv\Scripts\alembic.exe revision --autogenerate -m
    RUN_ROLLBACK = cd apps\api && .venv\Scripts\alembic.exe downgrade -1
    RUN_TEST_API = cd apps\api && .venv\Scripts\pytest.exe
    RUN_RUFF_FORMAT = apps\api\.venv\Scripts\ruff.exe format src/ tests/
    RUN_RUFF_LINT = apps\api\.venv\Scripts\ruff.exe check src/ tests/
else
    PYTHON = apps/api/.venv/bin/python
    PIP = apps/api/.venv/bin/pip
    ALEMBIC = apps/api/.venv/bin/alembic
    PYTEST = apps/api/.venv/bin/pytest
    RUFF = apps/api/.venv/bin/ruff
    COPY_ENV = test -f .env || cp .env.example .env
    CREATE_VENV = test -d apps/api/.venv || python -m venv apps/api/.venv
    CLEAN_CMD = rm -rf apps/web/.next node_modules apps/api/.pytest_cache
    RUN_MIGRATE = cd apps/api && .venv/bin/alembic upgrade head
    RUN_MIGRATE_CREATE = cd apps/api && .venv/bin/alembic revision --autogenerate -m
    RUN_ROLLBACK = cd apps/api && .venv/bin/alembic downgrade -1
    RUN_TEST_API = cd apps/api && .venv/bin/pytest
    RUN_RUFF_FORMAT = apps/api/.venv/bin/ruff format src/ tests/
    RUN_RUFF_LINT = apps/api/.venv/bin/ruff check src/ tests/
endif

.PHONY: help setup dev dev-infra dev-infra-down test test-api test-web lint format db-migrate db-migration db-rollback docker-build docker-up docker-down clean

# ── 1. Help Menu (Default) ──────────────────────────────────────────────────
help:
	@echo ========================================================================
	@echo 💗 Eralove — Command Menu (Makefile)
	@echo ========================================================================
	@echo Setup ^& Install:
	@echo   make setup              Install all project dependencies ^(Node ^& Python^)
	@echo.
	@echo Local Development:
	@echo   make dev                Start all local dev servers ^(Turborepo ^+ backend^)
	@echo   make dev-infra          Start infra containers ^(Postgres, Redis, MinIO, Mailpit^)
	@echo   make dev-infra-down     Stop and remove local infra containers
	@echo.
	@echo Database Migrations ^(Alembic^):
	@echo   make db-migrate         Run all migrations to upgrade database to head
	@echo   make db-migration msg="..." Create a new database migration auto-generated
	@echo   make db-rollback        Rollback last Alembic migration by -1
	@echo.
	@echo Testing:
	@echo   make test               Run both backend ^(pytest^) and frontend ^(vitest^) tests
	@echo   make test-api           Run backend ^(Python pytest^) tests
	@echo   make test-web           Run frontend ^(Vitest^) tests
	@echo.
	@echo Linting ^& Formatting:
	@echo   make lint               Lint and static check types across the project
	@echo   make format             Auto-format python and typescript code
	@echo.
	@echo Docker Production Deployment:
	@echo   make docker-build       Build API and Web production Docker images
	@echo   make docker-up          Run production stack with docker-compose
	@echo   make docker-down        Stop production docker-compose stack
	@echo.
	@echo Maintenance:
	@echo   make clean              Remove build caches, logs, and build artifacts
	@echo ========================================================================

# ── 2. Installation ──────────────────────────────────────────────────────────
setup:
	@echo [1/3] Copying environment templates...
	@$(COPY_ENV)
	@echo [2/3] Setting up Python virtual environment...
	@$(CREATE_VENV)
	@$(PIP) install -r apps/api/requirements-dev.txt
	@echo [3/3] Installing Node.js workspace dependencies...
	@npm install
	@echo 🎉 Eralove local setup completed!

# ── 3. Development ───────────────────────────────────────────────────────────
dev-infra:
	$(COMPOSE) -f $(INFRA_COMPOSE_FILE) up -d

dev-infra-down:
	$(COMPOSE) -f $(INFRA_COMPOSE_FILE) down

dev: dev-infra
	npm run dev

# ── 4. Database Migrations ───────────────────────────────────────────────────
db-migrate:
	$(RUN_MIGRATE)

db-migration:
ifndef msg
	$(error ❌ Error: msg variable is required. Run like: make db-migration msg="migration_name")
endif
	$(RUN_MIGRATE_CREATE) "$(msg)"

db-rollback:
	$(RUN_ROLLBACK)

# ── 5. Testing ───────────────────────────────────────────────────────────────
test: test-api test-web

test-api:
	$(RUN_TEST_API)

test-web:
	npm run test

# ── 6. Linting & Formatting ──────────────────────────────────────────────────
lint:
	npm run lint
	npm run type-check
	$(RUN_RUFF_LINT)

format:
	npm run format
	$(RUN_RUFF_FORMAT)

# ── 7. Docker production builds ──────────────────────────────────────────────
docker-build:
	@echo 🐳 Building Docker production images...
	docker build -f deploy/api.Dockerfile -t eralove-api:latest .
	docker build -f deploy/web.Dockerfile -t eralove-web:latest .
	@echo ✅ Production images built: eralove-api:latest, eralove-web:latest

docker-up:
	@echo 🚀 Launching Eralove production stack...
	$(COMPOSE) -f $(PROD_COMPOSE_FILE) up -d

docker-down:
	$(COMPOSE) -f $(PROD_COMPOSE_FILE) down

# ── 8. Cleanup ───────────────────────────────────────────────────────────────
clean:
	@echo 🧹 Cleaning cache, build artifacts and node_modules...
	@$(CLEAN_CMD)
	@echo ✅ Cleanup completed!
