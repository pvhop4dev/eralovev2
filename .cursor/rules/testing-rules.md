---
name: testing-rules
description: Testing strategy overview — references unit-testing.md for detailed patterns
---

# Testing Strategy

> Detailed unit testing patterns, factories, mocking rules → see `unit-testing.md`

## Test Pyramid

```
        /  E2E (Playwright)  \         — Few, critical flows only
       / Integration (httpx)  \        — API endpoints with real DB
      /   Unit (pytest/Vitest) \       — Bulk of tests, fast, isolated
```

## Backend Test Commands

```bash
# Unit tests (fast, mocked)
cd apps/api && pytest tests/unit -v

# Integration tests (needs Docker DB)
cd apps/api && pytest tests/integration -v

# All with coverage
cd apps/api && pytest --cov=src --cov-report=html --cov-fail-under=80
```

## Frontend Test Commands

```bash
# Component + hook tests
cd apps/web && npx vitest run

# Watch mode
cd apps/web && npx vitest

# Coverage
cd apps/web && npx vitest run --coverage
```

## E2E (Playwright)

```bash
# Run all E2E tests
cd apps/web && npx playwright test

# Run specific test
cd apps/web && npx playwright test e2e/auth.spec.ts

# UI mode (debug)
cd apps/web && npx playwright test --ui
```

## Critical E2E Flows

- Register → Verify Email → Login
- Onboarding wizard (4 steps)
- Search user → Send match → Accept match
- Create event with photos
- Send chat message → Receive in real-time
- Chat with Ari AI

## Integration Test Setup

```python
# tests/integration/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def db_session():
    """Transaction-scoped session that rolls back after each test."""
    async with engine.begin() as conn:
        async with AsyncSession(bind=conn) as session:
            yield session
            await conn.rollback()

@pytest.fixture
async def client(db_session):
    """Test HTTP client with overridden DB session."""
    app.dependency_overrides[get_session] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.fixture
async def auth_headers(client):
    """Register + login, return auth headers."""
    await client.post("/api/v1/auth/register", json={...})
    resp = await client.post("/api/v1/auth/login", json={...})
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## CI Pipeline (GitHub Actions)

```yaml
test:
  steps:
    - Backend lint: ruff check apps/api
    - Backend tests: pytest --cov-fail-under=80
    - Frontend lint: eslint apps/web
    - Frontend tests: vitest run
    - E2E tests: playwright test (on PR only)
```

## Test Naming

- Python: `test_{what}_{scenario}_{expected}` (e.g. `test_login_with_wrong_password_returns_401`)
- TypeScript: descriptive string (e.g. `"disables submit when form is empty"`)
- Files: `test_{module}.py` (Python), `{component}.test.tsx` (TypeScript)
