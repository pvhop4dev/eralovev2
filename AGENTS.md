# Eralove - Project Rules & Conventions

## Project Overview
Eralove is a private couples app — a romantic, AI-powered space for two people to store memories, connect daily, and receive love suggestions from AI mascot Ari.

## Tech Stack
- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS 4 + Framer Motion
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + Alembic
- **Database:** PostgreSQL 16 (primary) + Redis 7 (cache, pub/sub, sessions)
- **Storage:** AWS S3 (photos, videos, files) with presigned URLs
- **AI:** Claude API (Anthropic) for Mascot Ari
- **Realtime:** WebSocket (FastAPI WebSocket + Redis Pub/Sub)
- **Maps:** Mapbox GL JS
- **Auth:** JWT + OAuth2 (Google, Apple, Facebook)
- **Monorepo:** Turborepo

## Architecture: Clean Architecture

### Backend (Python)
```
apps/api/src/
├── domain/           # Entities, Value Objects, Repository Interfaces (NO external deps)
├── application/      # Use Cases, DTOs, Service Interfaces
├── infrastructure/   # DB repos, S3, Redis, External APIs, Email
└── presentation/     # FastAPI routes, middleware, WebSocket handlers
```

**Rules:**
- `domain/` MUST NOT import from any other layer
- `application/` can only import from `domain/`
- `infrastructure/` implements interfaces defined in `domain/` and `application/`
- `presentation/` depends on `application/` use cases via dependency injection
- Use `Depends()` for FastAPI dependency injection
- All database access goes through repository pattern

### Frontend (Next.js)
```
apps/web/src/
├── app/              # Next.js App Router pages & layouts
├── components/       # UI components (atomic design: atoms/molecules/organisms)
├── features/         # Feature modules (auth, calendar, chat, map, ari, etc.)
├── hooks/            # Custom React hooks
├── lib/              # Utilities, API client, constants
├── stores/           # Zustand stores
└── types/            # TypeScript type definitions
```

### Monorepo Structure
```
eralove/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # Python FastAPI backend
├── packages/
│   ├── ui/           # Shared UI component library
│   ├── shared/       # Shared types, constants, utils
│   └── config/       # Shared ESLint, Tailwind, TypeScript configs
├── infra/            # Docker, docker-compose, nginx, deployment configs
├── docs/             # Documentation & plans
├── scripts/          # Dev scripts, seed data, migrations
├── turbo.json
├── package.json
├── pyproject.toml
└── CLAUDE.md
```

## Coding Conventions

### Python (Backend)
- Use `async/await` for all I/O operations
- Type hints required on all function signatures
- Use Pydantic v2 for all DTOs and request/response schemas
- Use SQLAlchemy 2.0 style (mapped_column, select statements)
- Naming: `snake_case` for functions/variables, `PascalCase` for classes
- File naming: `snake_case.py`
- Tests with `pytest` + `pytest-asyncio`
- Use `Annotated[Depends()]` pattern for dependency injection
- Error handling: raise custom domain exceptions, map to HTTP in presentation layer
- Alembic for all database migrations (never modify DB schema manually)

### TypeScript (Frontend)
- Use functional components with hooks only (no class components)
- Use `"use client"` directive only when needed
- Server Components by default, Client Components only for interactivity
- Naming: `PascalCase` for components, `camelCase` for functions/variables
- File naming: `kebab-case.tsx` for components, `kebab-case.ts` for utils
- Use Zustand for client-side state management
- Use TanStack Query (React Query) for server state
- Use `next/image` for all images
- Use `next/font` for font loading (Nunito, Inter)
- Tailwind: Use design tokens from `tailwind.config.ts`, avoid arbitrary values
- All API calls go through a centralized API client (`lib/api-client.ts`)

### Shared Rules
- All environment variables in `.env.local` (frontend) and `.env` (backend)
- Never commit secrets or `.env` files
- Use ISO 8601 for all date/time formats in API
- Use UTC in backend, convert to local timezone in frontend
- Vietnamese language for user-facing content, English for code/comments
- All API responses follow format: `{ data, meta, error }`
- Pagination: cursor-based for feeds, offset-based for admin/search
- File uploads: presigned S3 URLs (never proxy through backend)

## Database Conventions
- Table names: `snake_case`, plural (e.g., `users`, `love_events`)
- Primary keys: UUID v7 (time-sortable)
- All tables have `created_at`, `updated_at` timestamps
- Soft delete with `deleted_at` column where applicable
- Use PostgreSQL JSONB for flexible metadata fields
- Index all foreign keys and frequently queried columns
- Use database-level constraints (NOT NULL, UNIQUE, CHECK, FK)

## Git Conventions
- Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`, `chore/`
- Commit messages: conventional commits format (feat:, fix:, refactor:, etc.)
- PRs require description with context
- One feature per PR, keep PRs small and focused

## Design System
- Colors: Rose Petal (#FF6B9D), Lavender Dream (#C084FC), Blush White (#FFF0F5), Deep Plum (#7C3AED), Peach Glow (#FFB347), Mint Fresh (#6EE7B7)
- Typography: Nunito (headings), Inter (body)
- Border radius: rounded-xl (12px) default for cards, rounded-full for buttons
- Shadows: soft shadows with pink/purple tint
- Animations: subtle, max 300ms for micro-interactions, 500ms for page transitions
- Dark mode: all components must support dark mode via Tailwind `dark:` prefix

## Domains
- **Frontend:** `https://love.eraquix.com`
- **Backend API:** `https://api-love.eraquix.com`
- **WebSocket:** `wss://api-love.eraquix.com/ws`
- **Local dev:** `http://localhost:3000` (web), `http://localhost:8000` (api)

## API Design
- RESTful endpoints under `/api/v1/`
- WebSocket at `/ws/`
- Auth endpoints at `/api/v1/auth/`
- Protected routes require Bearer token
- Rate limiting: 100 req/min for regular endpoints, 10 req/min for auth
- CORS: whitelist `love.eraquix.com` + `localhost:3000`
- OpenAPI docs available at `/docs` (dev only)

## Testing
- Backend: pytest with >80% coverage on use cases
- Frontend: Vitest + React Testing Library for components
- E2E: Playwright for critical flows
- Test naming: `test_<what>_<expected_behavior>`

## Performance
- Images: WebP format, lazy loading, responsive srcset
- API responses: compress with gzip/brotli
- Redis caching: cache weather, horoscope, daily quotes (TTL: 1 hour)
- Database: use connection pooling, optimize N+1 queries
- Frontend: dynamic imports for heavy components (map, chat)
