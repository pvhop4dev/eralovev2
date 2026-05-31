# Eralove — Feature Tracking & Progress

> **Last updated:** 2026-05-31
> **Legend:** ✅ Done | 🟡 Partial | ❌ Not Started | 🔵 Deferred

---

## Overview

| Phase | Target | Status | Completion |
|-------|--------|--------|------------|
| Phase 1 — MVP | Auth, Match, Dashboard, Calendar, Chat | 🟡 Partial | ~45% |
| Phase 2 — Core | Map, Ari AI, Quiz, Quests, Time Capsule | ❌ Not Started | 0% |
| Phase 3 — Polish | Shared Space, Secret Chat, Stickers, Export | ❌ Not Started | 0% |

---

## Phase 1 — MVP

### Sprint 1: Project Setup & Infrastructure

| # | Task | Backend | Frontend | Status |
|---|------|---------|----------|--------|
| 1.1 | Monorepo (Turborepo) | — | — | ✅ Done |
| 1.2 | Next.js scaffolding (App Router, TW4, Zustand, TanStack Query) | — | ✅ | ✅ Done |
| 1.3 | FastAPI scaffolding (Clean Architecture 4 layers) | ✅ | — | ✅ Done |
| 1.4 | Docker Compose (Postgres, Redis, MinIO, Mailpit) | ✅ | — | ✅ Done |
| — | SQLAlchemy 2.0 async + Alembic configured | ✅ | — | ✅ Done |
| — | Redis client + cache service | ✅ | — | ✅ Done |
| — | `turbo.json` configured | — | — | ✅ Done |
| — | `.env.example` | — | — | ✅ Done |
| — | Health check endpoint (`GET /api/v1/health`) | ✅ | — | ✅ Done |
| — | Alembic initial migration | — | — | ✅ Done |
| — | Seed script for dev data | — | — | ❌ Not Started |
| — | S3 client + presigned URL helper | — | — | ❌ Not Started |

**Sprint 1 Completion: ~83%**

---

### Sprint 2: Authentication

#### Backend Auth

| # | Task | Status | File |
|---|------|--------|------|
| 2.1 | `User` entity | ✅ | `domain/entities/user.py` |
| 2.2 | `Email` value object | ✅ | `domain/value_objects/email.py` |
| 2.3 | `Password` value object (bcrypt) | ✅ | `domain/value_objects/password.py` |
| 2.4 | `RegisterUser` use case | ✅ | `application/use_cases/auth/register.py` |
| 2.5 | `LoginUser` use case | ✅ | `application/use_cases/auth/login.py` |
| 2.6 | `VerifyEmail` use case | ✅ | `application/use_cases/auth/verify_email.py` |
| 2.7 | `UserRepository` (Postgres) | ✅ | `infrastructure/database/repositories/user_repository.py` |
| 2.8 | `JWTHandler` | ✅ | `infrastructure/auth/jwt_handler.py` |
| 2.9 | Auth routes (register, login) | ✅ | `presentation/api/v1/auth.py` |
| 2.10 | Email service (verification OTP) | ✅ | `infrastructure/email/email_service.py` |
| 2.11 | Auth DTO (Pydantic) | ✅ | `application/dtos/auth_dto.py` |
| 2.12 | Auth middleware (JWT Bearer) | ✅ | `presentation/middleware/auth_middleware.py` |
| 2.13 | `RefreshToken` model | ✅ | `infrastructure/database/models/refresh_token_model.py` |
| 2.14 | `OAuthAccount` model | ✅ | `infrastructure/database/models/oauth_account_model.py` |
| 2.15 | OAuth login use case (Google) | ❌ | — |
| 2.16 | Refresh token endpoint | ❌ | — |
| 2.17 | Rate limiting on auth (10 req/min) | ❌ | — |

#### Frontend Auth

| # | Task | Status | File |
|---|------|--------|------|
| 2.18 | Landing page (hero, CTA) | ✅ | `app/page.tsx` |
| 2.19 | Register page | ✅ | `app/(auth)/register/page.tsx` |
| 2.20 | Login page | ✅ | `app/(auth)/login/page.tsx` |
| 2.21 | Forgot password page | ✅ | `app/(auth)/forgot-password/page.tsx` |
| 2.22 | Email verification page | ✅ | `app/(auth)/verify-email/page.tsx` |
| 2.23 | Auth layout (shared) | ✅ | `app/(auth)/layout.tsx` |
| 2.24 | Auth store (Zustand) | ✅ | `stores/auth-store.ts` |
| 2.25 | Route protection middleware | ✅ | `middleware.ts` |
| 2.26 | Google OAuth integration | ❌ | — |

#### Shared UI Components

| # | Component | Status | File |
|---|-----------|--------|------|
| 2.27 | Button (variants) | ✅ | `components/atoms/button.tsx` |
| 2.28 | Input (text, email, password) | ✅ | `components/atoms/input.tsx` |
| 2.29 | FormField (label + error) | ✅ | `components/molecules/form-field.tsx` |
| 2.30 | Loading Spinner | ✅ | `components/atoms/loading-spinner.tsx` |
| 2.31 | Avatar | ✅ | `components/atoms/avatar.tsx` |
| 2.32 | Skeleton | ✅ | `components/atoms/skeleton.tsx` |
| 2.33 | Theme Toggle (dark mode) | ✅ | `components/atoms/theme-toggle.tsx` |
| 2.34 | Toast/Notification | ❌ | — (sonner installed but not wired) |
| 2.35 | Error Boundary | ✅ | `components/organisms/error-boundary.tsx` |

**Sprint 2 Completion: ~80%** (missing OAuth, refresh token, rate limiting)

---

### Sprint 3: Onboarding & Match System

#### Backend

| # | Task | Status | File |
|---|------|--------|------|
| 3.1 | `MatchRequest` entity | ✅ | `domain/entities/match_request.py` |
| 3.2 | `Couple` entity | ✅ | `domain/entities/couple.py` |
| 3.3 | `SendMatchRequest` use case | ✅ | `application/use_cases/match/send_request.py` |
| 3.4 | `AcceptMatch` use case | ✅ | `application/use_cases/match/accept_request.py` |
| 3.5 | `DeclineMatch` use case | ✅ | `application/use_cases/match/decline_request.py` |
| 3.6 | Match DTO | ✅ | `application/dtos/match_dto.py` |
| 3.7 | Match Repository (Postgres) | ✅ | `infrastructure/database/repositories/match_repository.py` |
| 3.8 | Couple Repository (Postgres) | ✅ | `infrastructure/database/repositories/couple_repository.py` |
| 3.9 | Match routes | ✅ | `presentation/api/v1/match.py` |
| 3.10 | Onboarding routes | ✅ | `presentation/api/v1/onboarding.py` |
| 3.11 | S3 presigned URL for avatar | ❌ | — |
| 3.12 | Unmatch use case | ❌ | — |

#### Frontend

| # | Task | Status | File |
|---|------|--------|------|
| 3.13 | Match page (search + send request) | ✅ | `app/(protected)/match/page.tsx` |
| 3.14 | Match requests inbox | 🟡 | `app/(protected)/match/requests/` (exists) |
| 3.15 | Onboarding wizard (multi-step) | ✅ | `app/(protected)/onboarding/page.tsx` |
| 3.16 | QR code match | ❌ | — |
| 3.17 | Love language quiz in onboarding | ❌ | — |
| 3.18 | Wallpaper chooser | ❌ | — |

**Sprint 3 Completion: ~65%**

---

### Sprint 4: Home Dashboard

#### Backend

| # | Task | Status | File |
|---|------|--------|------|
| 4.1 | Dashboard aggregated endpoint | ✅ | `presentation/api/v1/dashboard.py` |
| 4.2 | Daily love quote (500+ seeded, Redis cached) | ✅ | `infrastructure/quotes/love_quotes.py` |
| 4.3 | Mood check-in endpoint | ✅ | `presentation/api/v1/mood.py` |
| 4.4 | Days together calculation | ✅ | via dashboard endpoint |
| 4.5 | Memory flashback ("This day last year") | ❌ | — |

#### Frontend

| # | Task | Status | File |
|---|------|--------|------|
| 4.6 | Dashboard page (couple info, days counter) | ✅ | `app/(protected)/dashboard/page.tsx` |
| 4.7 | Quick shortcut grid (Calendar, Chat, Map, Ari) | ✅ | in dashboard |
| 4.8 | Daily love quote card | ✅ | in dashboard |
| 4.9 | Mood check-in widget | ✅ | in dashboard |
| 4.10 | Desktop sidebar navigation | ✅ | `components/organisms/sidebar.tsx` |
| 4.11 | Mobile bottom nav | ✅ | `components/organisms/bottom-nav.tsx` |
| 4.12 | Protected layout | ✅ | `app/(protected)/layout.tsx` |
| 4.13 | Notification dropdown | ❌ | — |
| 4.14 | Memory flashback card | ❌ | — |
| 4.15 | Upcoming events section | ❌ | — (API exists but not wired to dashboard) |

**Sprint 4 Completion: ~70%**

---

### Sprint 5: Love Calendar

#### Backend

| # | Task | Status | File |
|---|------|--------|------|
| 5.1 | `LoveEvent` entity | ✅ | `domain/entities/love_event.py` |
| 5.2 | Event Repository (Postgres) | ✅ | `infrastructure/database/repositories/event_repository.py` |
| 5.3 | Events CRUD routes | ✅ | `presentation/api/v1/events.py` |
| 5.4 | Event types (date, anniversary, travel, birthday) | ✅ | in entity |
| 5.5 | Get by month, upcoming, by ID | ✅ | in events routes |
| 5.6 | Soft delete | ✅ | in events routes |
| 5.7 | `Photo` entity + S3 upload flow | ❌ | — |
| 5.8 | Attach photos to events | ❌ | — |
| 5.9 | Recurring events | ❌ | — |

#### Frontend

| # | Task | Status | File |
|---|------|--------|------|
| 5.10 | Calendar page (month view) | ✅ | `app/(protected)/calendar/page.tsx` |
| 5.11 | Week view | ❌ | — |
| 5.12 | Day detail modal | ❌ | — |
| 5.13 | Create event form | 🟡 | Basic form exists |
| 5.14 | Photo upload to events | ❌ | — |
| 5.15 | Edit/delete event | 🟡 | API exists, UI unclear |
| 5.16 | Event icons by type | ❌ | — |
| 5.17 | Location picker | ❌ | — |
| 5.18 | Reminder settings | ❌ | — |

**Sprint 5 Completion: ~40%**

---

### Sprint 6: Chat & Love Touch

#### Backend

| # | Task | Status | File |
|---|------|--------|------|
| 6.1 | `Message` entity | ✅ | `domain/entities/message.py` |
| 6.2 | Message Repository (Postgres) | ✅ | `infrastructure/database/repositories/message_repository.py` |
| 6.3 | Messages CRUD routes (REST) | ✅ | `presentation/api/v1/messages.py` |
| 6.4 | Pin/Unpin message | ✅ | in messages routes |
| 6.5 | Mark as read | ✅ | in messages routes |
| 6.6 | Soft delete | ✅ | in messages routes |
| 6.7 | Cursor-based pagination | ✅ | in messages routes |
| 6.8 | WebSocket handler + JWT auth | ❌ | — |
| 6.9 | Redis Pub/Sub for real-time | ❌ | — |
| 6.10 | Typing indicator | ❌ | — |
| 6.11 | Message reactions | ❌ | — |
| 6.12 | Love Touch WebSocket event | ❌ | — |
| 6.13 | Push notification | ❌ | — |

#### Frontend

| # | Task | Status | File |
|---|------|--------|------|
| 6.14 | Chat page (basic UI) | ✅ | `app/(protected)/chat/page.tsx` |
| 6.15 | Chat bubbles (pink/purple) | 🟡 | Basic implementation |
| 6.16 | WebSocket connection manager | ❌ | — |
| 6.17 | Real-time message receive | ❌ | — |
| 6.18 | Image upload in chat | ❌ | — |
| 6.19 | Voice message | ❌ | — |
| 6.20 | Emoji picker | ❌ | — |
| 6.21 | Message reactions | ❌ | — |
| 6.22 | Reply to message | ❌ | — |
| 6.23 | Typing indicator | ❌ | — |
| 6.24 | Read receipts | ❌ | — |
| 6.25 | Love Touch button | ❌ | — |
| 6.26 | Online/offline status | ❌ | — |

**Sprint 6 Completion: ~30%** (REST API done, no real-time)

---

### Sprint 7: Polish & Testing

#### Testing

| # | Task | Status | Details |
|---|------|--------|---------|
| 7.1 | Domain entity unit tests | ✅ | 7 test files (user, couple, event, message, match, email, password) |
| 7.2 | Infrastructure unit tests | ✅ | 3 test files (JWT, quotes, trace context) |
| 7.3 | Use case unit tests | ✅ | 5 test files (register, login, send/accept/decline match) |
| 7.4 | Integration tests | ❌ | Only `__init__.py` exists |
| 7.5 | Frontend component tests (Vitest) | ❌ | Not configured |
| 7.6 | E2E tests (Playwright) | ❌ | Not configured |

#### Infrastructure & DevOps

| # | Task | Status |
|---|------|--------|
| 7.7 | GZip compression middleware | ✅ |
| 7.8 | Trace middleware (X-Trace-Id) | ✅ |
| 7.9 | Domain exception → HTTP mapping | ✅ |
| 7.10 | Validation error handler | ✅ |
| 7.11 | CORS configuration | ✅ |
| 7.12 | API docs (dev only) | ✅ |
| 7.13 | Dockerfile (API) | ✅ |
| 7.14 | CI/CD (GitHub Actions) | ❌ |
| 7.15 | Vercel deployment (frontend) | ❌ |
| 7.16 | Backend deployment (Railway/Fly) | ❌ |
| 7.17 | Domain setup (love.eraquix.com) | ❌ |
| 7.18 | PWA manifest + service worker | ❌ |

**Sprint 7 Completion: ~35%**

---

## Phase 2 — Core Features

| Sprint | Feature | Status |
|--------|---------|--------|
| 8 | Calendar Header Widget (weather, horoscope, feng shui) | ❌ |
| 8 | Calendar year view + search | ❌ |
| 9 | Love Map (Mapbox, pins, heatmap, journey) | ❌ |
| 9 | Live location sharing | ❌ |
| 9 | Travel statistics & badges | ❌ |
| 10 | AI Mascot Ari chatbot (Claude API) | ❌ |
| 10 | Ari daily check-in | ❌ |
| 10 | Ari weekly love report | ❌ |
| 11 | Ari virtual pet (happiness, health) | ❌ |
| 11 | AI sentiment analysis | ❌ |
| 11 | Accessory shop (love coins) | ❌ |
| 12 | Daily love quiz | ❌ |
| 12 | Weekly love quests | ❌ |
| 12 | Love coins system | ❌ |
| 13 | Time capsule | ❌ |
| 13 | Voice & video call (WebRTC) | ❌ |

---

## Phase 3 — Deep Features

| Feature | Status |
|---------|--------|
| Shared Notes & To-do Lists | ❌ |
| Date Fund (expense tracker) | ❌ |
| Secret Chat (blur + scratch reveal) | ❌ |
| Draw Together (canvas in chat) | ❌ |
| App icon customizer | ❌ |
| Custom wallpapers per screen | ❌ |
| Font & color theme picker | ❌ |
| Sticker shop + GIPHY | ❌ |
| Data export as ZIP (Celery) | ❌ |
| Anniversary auto-generated cards | ❌ |
| Achievement badges system | ❌ |

---

## Architecture & Code Quality

| Area | Status | Details |
|------|--------|---------|
| Clean Architecture (4 layers) | ✅ | domain → application → infrastructure → presentation |
| Repository pattern | ✅ | 5 domain interfaces + 5 Postgres implementations |
| Dependency injection (FastAPI Depends) | 🟡 | Some routes still instantiate repos directly |
| Pydantic v2 DTOs | 🟡 | Auth & Match DTOs done; Events & Messages use inline schemas |
| Use Case pattern (single `execute`) | 🟡 | Auth & Match have proper use cases; Events & Messages bypass |
| SQLAlchemy 2.0 models | ✅ | 7 models (user, couple, event, message, match, oauth, refresh_token) |
| Alembic migrations | ❌ | Configured but no actual migration versions |
| API response format `{data, meta, error}` | ✅ | Consistent across all routes |
| Cursor-based pagination | ✅ | Messages endpoint |
| Structured logging | 🟡 | structlog imported but not consistently used |
| UUID v7 primary keys | ❌ | Using UUID v4 |

---

## Frontend Architecture

| Area | Status | Details |
|------|--------|---------|
| Atomic Design (atoms/molecules/organisms) | ✅ | 6 atoms, 1 molecule, 3 organisms |
| Zustand store | 🟡 | Only `auth-store.ts` exists |
| TanStack Query integration | ❌ | Installed but not used (raw `fetch` calls) |
| API client (`lib/api-client.ts`) | ✅ | Created with interceptors |
| Framer Motion animations | 🟡 | Installed, minimal usage |
| Dark mode (next-themes) | ✅ | ThemeToggle component + CSS variables |
| Responsive design | 🟡 | Basic responsive, not fully QA'd |
| `next/image` for images | ❌ | Not used yet |
| `next/font` for Nunito + Inter | 🟡 | Partially configured |
| Feature modules structure | ❌ | No `features/` directory yet |
| Design system tokens (Tailwind config) | 🟡 | CSS variables exist, not fully tokenized |

---

## Database Models (Existing)

| Model | Table | Soft Delete | Timestamps | File |
|-------|-------|-------------|------------|------|
| `UserModel` | `users` | ❌ | ✅ | `models/user_model.py` |
| `CoupleModel` | `couples` | ❌ | ✅ | `models/couple_model.py` |
| `LoveEventModel` | `love_events` | ✅ | ✅ | `models/love_event_model.py` |
| `MessageModel` | `messages` | ✅ | ✅ | `models/message_model.py` |
| `MatchRequestModel` | `match_requests` | ❌ | ✅ | `models/match_request_model.py` |
| `OAuthAccountModel` | `oauth_accounts` | ❌ | ✅ | `models/oauth_account_model.py` |
| `RefreshTokenModel` | `refresh_tokens` | ❌ | ✅ | `models/refresh_token_model.py` |

**Missing models:** Photos, MoodCheckin, Notification, Quiz, Quest, LoveCoin, TimeCapsule, Sticker, SharedNote, TodoList, DateFund, AriConversation, AriMessage

---

## API Endpoints (Existing)

| Router | Prefix | Methods | File |
|--------|--------|---------|------|
| Health | `/api/v1/health` | GET | `v1/health.py` |
| Auth | `/api/v1/auth` | POST register, login | `v1/auth.py` |
| Users | `/api/v1/users` | GET me, PATCH profile | `v1/users.py` |
| Match | `/api/v1/match` | POST send, accept, decline; GET requests | `v1/match.py` |
| Couple | `/api/v1/couple` | GET info | `v1/couple.py` |
| Onboarding | `/api/v1/onboarding` | POST complete | `v1/onboarding.py` |
| Dashboard | `/api/v1/dashboard` | GET aggregated | `v1/dashboard.py` |
| Mood | `/api/v1/mood` | POST checkin | `v1/mood.py` |
| Events | `/api/v1/events` | GET list, GET upcoming, GET by ID, POST create, PATCH update, DELETE | `v1/events.py` |
| Messages | `/api/v1/messages` | GET list, GET pinned, POST send, POST read, POST pin, DELETE | `v1/messages.py` |

**Missing endpoints:** OAuth, refresh token, photos, WebSocket, Ari AI, quiz, quests, coins, time capsule, notifications, settings, shared space

---

## Tests (Existing)

| Category | Count | Files |
|----------|-------|-------|
| Domain entity tests | 7 | user, couple, love_event, message, match_request, email VO, password VO |
| Infrastructure tests | 3 | jwt_handler, love_quotes, trace_context |
| Use case tests | 5 | register, login, send_request, accept_request, decline_request |
| Integration tests | 0 | — |
| Frontend tests | 0 | — |
| E2E tests | 0 | — |
| **Total** | **15** | |

---

## Priority Backlog (Recommended Next Steps)

### 🔴 Critical (must-do for MVP)

1. **Alembic migrations** — Create actual migration versions so DB schema can be deployed
2. **WebSocket for chat** — Chat is unusable without real-time
3. **OAuth (Google)** — Required for easy onboarding
4. **Token refresh endpoint** — Auth breaks after 15min without this
5. **TanStack Query migration** — Replace raw `fetch` with proper server state management
6. **Photo upload flow (S3)** — Core feature for calendar events

### 🟡 Important (before launch)

7. **Use Case refactoring** — Events & Messages routes should go through proper use cases
8. **DTO consolidation** — Move inline Pydantic schemas to `application/dtos/`
9. **Frontend feature modules** — Create `features/` directory structure
10. **More Zustand stores** — Chat, calendar, couple, notifications
11. **Integration tests** — Auth flow end-to-end
12. **Rate limiting** — Auth endpoints need 10 req/min limit
13. **CI/CD pipeline** — GitHub Actions for lint/test/build

### 🟢 Nice to have (post-MVP)

14. **PWA manifest** — Installable web app
15. **Push notifications** — Firebase/Web Push
16. **Framer Motion polish** — Page transitions, micro-animations
17. **SEO optimization** — Meta tags for public pages
