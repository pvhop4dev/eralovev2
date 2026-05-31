---
name: create-feature
description: Scaffold a new feature module for Eralove (backend + frontend)
---

# Create Feature Skill

When the user asks to create a new feature, follow this process:

## 1. Backend (Python FastAPI - Clean Architecture)

Create the following files for the feature:

### Domain Layer
- `apps/api/src/domain/entities/{feature}.py` — Entity class with business rules
- `apps/api/src/domain/repositories/{feature}_repository.py` — Abstract repository interface (ABC)

### Application Layer
- `apps/api/src/application/use_cases/{feature}/` — One file per use case
- `apps/api/src/application/dtos/{feature}_dto.py` — Pydantic request/response schemas

### Infrastructure Layer
- `apps/api/src/infrastructure/database/models/{feature}_model.py` — SQLAlchemy model
- `apps/api/src/infrastructure/database/repositories/{feature}_repository.py` — Concrete repository

### Presentation Layer
- `apps/api/src/presentation/api/v1/{feature}.py` — FastAPI router with endpoints

### Migration
- Run `alembic revision --autogenerate -m "add {feature} tables"`

### Tests
- `apps/api/tests/unit/use_cases/test_{feature}.py`
- `apps/api/tests/integration/test_{feature}_api.py`

## 2. Frontend (Next.js)

### Pages
- `apps/web/src/app/(main)/{feature}/page.tsx` — Main page (Server Component)
- `apps/web/src/app/(main)/{feature}/[id]/page.tsx` — Detail page (if needed)

### Feature Module
- `apps/web/src/features/{feature}/components/` — Feature-specific components
- `apps/web/src/features/{feature}/hooks/` — Feature-specific hooks
- `apps/web/src/features/{feature}/api.ts` — API functions (TanStack Query)
- `apps/web/src/features/{feature}/types.ts` — TypeScript types

## 3. Checklist
- [ ] Entity follows domain rules (no external dependencies)
- [ ] Repository interface is abstract (in domain layer)
- [ ] Use cases are single-purpose
- [ ] DTOs use Pydantic v2 with validation
- [ ] API routes use dependency injection
- [ ] Frontend uses Server Components where possible
- [ ] API calls go through centralized API client
- [ ] Loading and error states handled
- [ ] Dark mode supported
- [ ] Mobile responsive
