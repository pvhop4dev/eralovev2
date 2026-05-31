# Eralove - Phase 1: MVP Implementation Plan

## Goal
Deliver core couples experience: Auth, Match, Dashboard, Calendar (basic), Chat with Love Touch.

## Timeline: Sprint-based (2-week sprints)

---

## Sprint 1: Project Setup & Infrastructure (Week 1-2)

### Tasks

#### 1.1 Monorepo Setup
- [x] Initialize Turborepo with `apps/web`, `apps/api`, `packages/`
- [x] Configure `turbo.json` with build/dev/lint/test pipelines
- [x] Root `package.json` with workspace scripts
- [x] Root `pyproject.toml` for Python workspace

#### 1.2 Frontend Scaffolding (Next.js)
- [x] `npx create-next-app@latest` with App Router, TypeScript, Tailwind
- [x] Configure Tailwind with Eralove design tokens (colors, fonts, spacing)
- [x] Install & configure: Zustand, TanStack Query, Framer Motion, next-intl
- [x] Setup `next/font` for Nunito + Inter
- [x] Create base layout with metadata
- [x] Setup API client (`lib/api-client.ts`) with interceptors for auth
- [x] Setup ESLint + Prettier configs

#### 1.3 Backend Scaffolding (Python FastAPI)
- [x] Initialize FastAPI project with `pyproject.toml`
- [x] Setup project structure (domain/application/infrastructure/presentation)
- [x] Configure SQLAlchemy 2.0 async engine + session
- [x] Configure Alembic for migrations
- [x] Setup Redis client
- [ ] Setup S3 client (boto3) with presigned URL helper
- [x] Setup dependency injection container
- [x] Configure CORS, rate limiter middleware
- [x] Setup pytest + pytest-asyncio
- [x] Dockerfile for development

#### 1.4 Infrastructure
- [x] `docker-compose.yml` with PostgreSQL, Redis, MinIO (local S3), Mailpit
- [x] Create initial Alembic migration (users table)
- [ ] Seed script for development data
- [x] `.env.example` with all required variables
- [x] `.gitignore` for both Python and Node.js

#### Deliverable
- `turbo dev` starts both frontend (port 3000) and backend (port 8000)
- PostgreSQL, Redis, MinIO running in Docker
- Health check endpoint: `GET /api/v1/health`

---

## Sprint 2: Authentication (Week 3-4)

### Tasks

#### 2.1 Backend: Auth Domain & Use Cases
- [ ] Domain: `User` entity, `Email` and `Password` value objects
- [ ] Use Cases: `RegisterUser`, `LoginUser`, `OAuthLogin`, `RefreshToken`
- [ ] Infrastructure: `UserRepository` (PostgreSQL), `JWTHandler`, `OAuthProviders`
- [ ] Presentation: Auth routes (`/auth/register`, `/auth/login`, `/auth/oauth`, `/auth/refresh`, `/auth/logout`)
- [ ] Email verification with OTP (6-digit code)
- [ ] Password hashing with bcrypt
- [ ] JWT access token (15min) + refresh token (7 days, httpOnly cookie)
- [ ] Rate limiting on auth endpoints (10 req/min)

#### 2.2 Frontend: Auth Pages
- [ ] Welcome/Landing page with hero animation, feature highlights, CTA
- [ ] Register page (email, password, display_name, DOB, gender)
- [ ] Login page (email/password + social login buttons)
- [ ] Forgot password page
- [ ] Email verification page (OTP input)
- [ ] Auth store (Zustand) for token management
- [ ] Protected route middleware (Next.js middleware.ts)
- [ ] Google OAuth integration (frontend + backend)

#### 2.3 Shared UI Components
- [ ] Button (variants: primary, secondary, outline, ghost)
- [ ] Input (text, email, password with show/hide, date)
- [ ] Form field with label + error message
- [ ] Loading spinner (heart animation)
- [ ] Toast notification component
- [ ] Avatar component

#### Deliverable
- User can register, verify email, login, logout
- Google OAuth login works
- Protected routes redirect to login
- JWT tokens refresh automatically

---

## Sprint 3: Onboarding & Match System (Week 5-6)

### Tasks

#### 3.1 Backend: Onboarding
- [ ] Use Case: `CompleteOnboarding` (save profile, love language, avatar)
- [ ] S3 presigned URL for avatar upload
- [ ] Update user `is_onboarded` flag

#### 3.2 Backend: Match System
- [ ] Domain: `MatchRequest` entity, `Couple` entity
- [ ] Use Cases: `SendMatchRequest`, `AcceptMatch`, `DeclineMatch`, `Unmatch`
- [ ] Domain rule: one active match per user at a time
- [ ] Match request expiry (7 days)
- [ ] Create `couples` record on accept with `start_date`
- [ ] Soft unmatch (hide data, don't delete)

#### 3.3 Frontend: Onboarding Flow
- [ ] Step 1: Welcome + display name
- [ ] Step 2: Avatar upload + DOB (for zodiac)
- [ ] Step 3: Mini love language quiz (3 questions)
- [ ] Step 4: Choose default wallpaper
- [ ] Progress bar (heart steps)
- [ ] Framer Motion page transitions

#### 3.4 Frontend: Match System
- [ ] Search user page (by username/email)
- [ ] User profile preview card
- [ ] Send match request with custom message
- [ ] Match requests inbox (sent & received)
- [ ] Accept flow: choose start date, confetti animation
- [ ] Decline flow: gentle rejection
- [ ] QR code generation & scanner for quick match

#### Deliverable
- New user goes through onboarding wizard
- Can search and send match request
- Partner can accept with start date
- Love Space created, redirect to dashboard

---

## Sprint 4: Home Dashboard (Week 7-8)

### Tasks

#### 4.1 Backend: Dashboard API
- [ ] Aggregated `GET /dashboard` endpoint
- [ ] Days together calculation from `couples.start_date`
- [ ] Daily love quote (cached in Redis, 500+ quotes seeded)
- [ ] Upcoming events (next 7 days)
- [ ] Memory flashback ("This day last year...")
- [ ] Mood check-in endpoints

#### 4.2 Frontend: Dashboard
- [ ] Couple photo + names + days counter ("365 ngay")
- [ ] Quick shortcut grid (Calendar, Map, Chat, Ari)
- [ ] Daily love card with quote
- [ ] Upcoming events section
- [ ] Memory flashback card (if applicable)
- [ ] Mood check-in widget (emoji picker for both users)
- [ ] Responsive layout (desktop sidebar + mobile bottom nav)

#### 4.3 Navigation & Layout
- [ ] Desktop: Sidebar navigation with icons
- [ ] Mobile: Bottom tab navigation
- [ ] Header with couple avatar + notification bell
- [ ] Notification dropdown (basic)
- [ ] Dark mode toggle

#### Deliverable
- Dashboard shows couple info, daily quote, mood check-in
- Navigation works on desktop and mobile
- Dark mode works throughout app

---

## Sprint 5: Love Calendar — Basic (Week 9-10)

### Tasks

#### 5.1 Backend: Events & Photos
- [ ] Domain: `LoveEvent` entity, `Photo` entity
- [ ] Use Cases: CRUD events, upload photos, attach photos to events
- [ ] S3 presigned URL flow for photo upload
- [ ] Event types: date, anniversary, travel, birthday, custom
- [ ] Recurring events (yearly anniversaries)
- [ ] Soft delete with 30-day recovery

#### 5.2 Frontend: Calendar View
- [ ] Month view with event indicators (icons by type)
- [ ] Week view
- [ ] Swipe/click to navigate months
- [ ] Day detail modal: list events + photos for that day
- [ ] Event icons: camera (photos), heart (event), cake (birthday), ring (anniversary)

#### 5.3 Frontend: Event Management
- [ ] Create event form (title, type, date, time, location, description)
- [ ] Location picker (text input + optional map pin)
- [ ] Photo upload (drag & drop / file picker, max 20 per event)
- [ ] Photo grid view with caption
- [ ] Edit event form
- [ ] Delete event with confirmation
- [ ] Reminder settings (1 day, 1 week before)

#### Deliverable
- Calendar shows events with type-specific icons
- Create/edit/delete events with photos
- Events linked to locations (text-based for now)

---

## Sprint 6: Chat & Love Touch (Week 11-12)

### Tasks

#### 6.1 Backend: Realtime Chat
- [ ] Domain: `Message` entity
- [ ] WebSocket handler with JWT auth
- [ ] Redis Pub/Sub for message broadcasting
- [ ] Message persistence to PostgreSQL
- [ ] Message types: text, image, voice, love_message
- [ ] Message status: sent → delivered → read
- [ ] Typing indicator via WebSocket
- [ ] Pin/unpin messages
- [ ] Delete message (for me / for both)
- [ ] Reactions (emoji)

#### 6.2 Backend: Love Touch
- [ ] WebSocket event: `love_touch`
- [ ] Push notification when partner offline

#### 6.3 Frontend: Chat Interface
- [ ] Chat bubble layout (pink/purple theme)
- [ ] Text input with send button
- [ ] Image upload in chat
- [ ] Voice message (hold to record)
- [ ] Emoji picker
- [ ] Message reactions (long press)
- [ ] Reply to message (quote)
- [ ] Typing indicator
- [ ] Read receipts (double check marks)
- [ ] Pin message
- [ ] Love Message: special card style with heart animation
- [ ] Love Touch button: hold to send heartbeat vibration
- [ ] Scroll to bottom, load more on scroll up

#### 6.4 Frontend: Real-time
- [ ] WebSocket connection manager
- [ ] Auto-reconnect on disconnect
- [ ] Online/offline status indicator
- [ ] Unread message count badge

#### Deliverable
- Real-time chat between couple
- Send text, images, voice messages
- Love Touch sends vibration to partner
- Message reactions, replies, pinning

---

## Sprint 7: Polish & Testing (Week 13-14)

### Tasks

#### 7.1 Testing
- [ ] Backend: Unit tests for all use cases (>80% coverage)
- [ ] Backend: Integration tests for auth flow
- [ ] Frontend: Component tests for key UI components
- [ ] E2E: Playwright tests for critical flows
  - Register → Onboard → Match → Dashboard → Create Event → Chat

#### 7.2 Performance & Security
- [ ] API response compression (gzip)
- [ ] Image optimization (WebP, lazy loading)
- [ ] SQL query optimization (check N+1)
- [ ] Security audit: XSS, CSRF, SQL injection checks
- [ ] Rate limiting verification
- [ ] Error handling & logging (structured logs)

#### 7.3 Polish
- [ ] Loading states & skeletons for all pages
- [ ] Error boundaries & fallback UI
- [ ] Empty states (no events, no messages)
- [ ] Animations refinement (Framer Motion)
- [ ] SEO metadata for public pages
- [ ] PWA manifest & service worker basics
- [ ] Responsive design QA (375px, 768px, 1440px)

#### 7.4 Deployment Setup
- [ ] Vercel deployment for frontend
- [ ] Backend deployment (Railway/Render/Fly.io)
- [ ] PostgreSQL hosted (Supabase/Neon)
- [ ] Redis hosted (Upstash)
- [ ] S3 bucket + CloudFront CDN
- [ ] Environment variables configured
- [ ] CI/CD: GitHub Actions (lint, test, build, deploy)
- [ ] Domain setup (love.eraquix.com + api-love.eraquix.com)

#### Deliverable
- MVP deployed and accessible
- Core flows working end-to-end
- Automated tests passing in CI

---

## MVP Feature Summary

| Feature | Status |
|---|---|
| Welcome & Landing Page | Phase 1 |
| Email & Google Auth | Phase 1 |
| Onboarding Wizard | Phase 1 |
| Match System (search, request, accept) | Phase 1 |
| Home Dashboard | Phase 1 |
| Love Calendar (basic CRUD) | Phase 1 |
| Photo Upload to Events | Phase 1 |
| Real-time Chat | Phase 1 |
| Love Touch | Phase 1 |
| Message Reactions & Replies | Phase 1 |
| Mood Check-in | Phase 1 |
| Dark Mode | Phase 1 |
| Responsive Design | Phase 1 |

## Deferred to Phase 2
- Calendar header widget (weather, horoscope, feng shui)
- Love Map
- Voice & Video Call
- Mascot Ari AI
- Daily Quiz & Quests
- Smart Suggestions
- Time Capsule
- Shared Space
- Secret Chat / Draw Together
- OS Widgets
