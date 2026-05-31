# Eralove - Architecture Plan

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Next.js Web  │  │ React Native │  │   OS Widgets     │  │
│  │  (App Router) │  │   (Future)   │  │ (iOS/Android)    │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY / CDN                      │
│     love.eraquix.com (Web) + CloudFront (S3)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  REST API    │ │  WebSocket   │ │  S3 Presigned│
│  /api/v1/*   │ │  /ws/*       │ │  Upload URLs │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
┌──────┴────────────────┴────────────────┴────────┐
│                  BACKEND (Python FastAPI)         │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │              PRESENTATION LAYER              │ │
│  │  Routes, Middleware, WebSocket Handlers,     │ │
│  │  Auth Guards, Request Validation             │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                             │
│  ┌──────────────────▼──────────────────────────┐ │
│  │              APPLICATION LAYER               │ │
│  │  Use Cases, DTOs, Service Interfaces,        │ │
│  │  Event Handlers, Background Tasks            │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                             │
│  ┌──────────────────▼──────────────────────────┐ │
│  │                DOMAIN LAYER                  │ │
│  │  Entities, Value Objects, Domain Events,     │ │
│  │  Repository Interfaces, Domain Services      │ │
│  └─────────────────────────────────────────────┘ │
│                     │                             │
│  ┌──────────────────▼──────────────────────────┐ │
│  │            INFRASTRUCTURE LAYER              │ │
│  │  PostgreSQL Repos, Redis Cache, S3 Client,  │ │
│  │  Claude API, Mapbox, Weather API, Email,     │ │
│  │  FCM Push, OAuth Providers                   │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
          │           │           │
          ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│PostgreSQL│ │  Redis   │ │  AWS S3  │
│  (Data)  │ │(Cache/WS)│ │ (Files)  │
└──────────┘ └──────────┘ └──────────┘
```

## 2. Monorepo Structure (Turborepo)

```
eralove/
├── apps/
│   ├── web/                          # Next.js 15 App
│   │   ├── src/
│   │   │   ├── app/                  # App Router
│   │   │   │   ├── (auth)/           # Auth group: login, register, forgot-password
│   │   │   │   ├── (onboarding)/     # Onboarding wizard
│   │   │   │   ├── (main)/           # Main app group (requires auth)
│   │   │   │   │   ├── dashboard/    # Home dashboard
│   │   │   │   │   ├── calendar/     # Love Calendar
│   │   │   │   │   ├── map/          # Love Map
│   │   │   │   │   ├── chat/         # Chat & Call
│   │   │   │   │   ├── ari/          # Mascot Ari
│   │   │   │   │   ├── quests/       # Love Quests & Quiz
│   │   │   │   │   ├── shared-space/ # Shared notes, todos, fund
│   │   │   │   │   ├── suggestions/  # Smart Suggestions
│   │   │   │   │   └── settings/     # Settings & Profile
│   │   │   │   ├── layout.tsx
│   │   │   │   └── page.tsx          # Welcome/Landing page
│   │   │   ├── components/
│   │   │   │   ├── atoms/            # Button, Input, Badge, Avatar...
│   │   │   │   ├── molecules/        # Card, FormField, SearchBar...
│   │   │   │   └── organisms/        # Header, Sidebar, ChatBubble...
│   │   │   ├── features/
│   │   │   │   ├── auth/
│   │   │   │   ├── calendar/
│   │   │   │   ├── chat/
│   │   │   │   ├── map/
│   │   │   │   ├── ari/
│   │   │   │   ├── quests/
│   │   │   │   ├── shared-space/
│   │   │   │   └── suggestions/
│   │   │   ├── hooks/
│   │   │   ├── lib/
│   │   │   │   ├── api-client.ts     # Centralized API client
│   │   │   │   ├── auth.ts           # Auth utilities
│   │   │   │   ├── websocket.ts      # WebSocket client
│   │   │   │   ├── s3.ts             # S3 presigned URL helper
│   │   │   │   └── constants.ts
│   │   │   ├── stores/               # Zustand stores
│   │   │   └── types/
│   │   ├── public/
│   │   ├── next.config.ts
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   └── package.json
│   │
│   └── api/                          # Python FastAPI Backend
│       ├── src/
│       │   ├── domain/
│       │   │   ├── entities/
│       │   │   │   ├── user.py
│       │   │   │   ├── couple.py
│       │   │   │   ├── event.py
│       │   │   │   ├── message.py
│       │   │   │   ├── photo.py
│       │   │   │   ├── location.py
│       │   │   │   ├── quest.py
│       │   │   │   ├── quiz.py
│       │   │   │   └── ari_conversation.py
│       │   │   ├── value_objects/
│       │   │   │   ├── email.py
│       │   │   │   ├── password.py
│       │   │   │   ├── love_language.py
│       │   │   │   └── mood.py
│       │   │   ├── events/           # Domain events
│       │   │   │   ├── couple_matched.py
│       │   │   │   ├── event_created.py
│       │   │   │   └── message_sent.py
│       │   │   ├── repositories/     # Abstract repository interfaces
│       │   │   │   ├── user_repository.py
│       │   │   │   ├── couple_repository.py
│       │   │   │   ├── event_repository.py
│       │   │   │   └── message_repository.py
│       │   │   └── services/         # Domain services
│       │   │       ├── match_service.py
│       │   │       └── love_counter.py
│       │   │
│       │   ├── application/
│       │   │   ├── use_cases/
│       │   │   │   ├── auth/
│       │   │   │   │   ├── register.py
│       │   │   │   │   ├── login.py
│       │   │   │   │   ├── oauth_login.py
│       │   │   │   │   └── refresh_token.py
│       │   │   │   ├── match/
│       │   │   │   │   ├── send_match_request.py
│       │   │   │   │   ├── accept_match.py
│       │   │   │   │   ├── decline_match.py
│       │   │   │   │   └── unmatch.py
│       │   │   │   ├── calendar/
│       │   │   │   │   ├── create_event.py
│       │   │   │   │   ├── update_event.py
│       │   │   │   │   ├── delete_event.py
│       │   │   │   │   └── get_events.py
│       │   │   │   ├── chat/
│       │   │   │   │   ├── send_message.py
│       │   │   │   │   ├── get_messages.py
│       │   │   │   │   └── pin_message.py
│       │   │   │   ├── photo/
│       │   │   │   │   ├── upload_photo.py
│       │   │   │   │   └── get_photos.py
│       │   │   │   ├── ari/
│       │   │   │   │   ├── chat_with_ari.py
│       │   │   │   │   └── daily_checkin.py
│       │   │   │   ├── quest/
│       │   │   │   │   ├── get_daily_quiz.py
│       │   │   │   │   ├── submit_quiz_answer.py
│       │   │   │   │   └── complete_quest.py
│       │   │   │   └── suggestion/
│       │   │   │       ├── get_gift_suggestions.py
│       │   │   │       └── get_date_suggestions.py
│       │   │   ├── dtos/
│       │   │   └── interfaces/       # Service interfaces
│       │   │       ├── ai_service.py
│       │   │       ├── storage_service.py
│       │   │       ├── weather_service.py
│       │   │       ├── notification_service.py
│       │   │       └── horoscope_service.py
│       │   │
│       │   ├── infrastructure/
│       │   │   ├── database/
│       │   │   │   ├── connection.py
│       │   │   │   ├── models/       # SQLAlchemy models
│       │   │   │   └── repositories/ # Concrete repository implementations
│       │   │   ├── cache/
│       │   │   │   └── redis_client.py
│       │   │   ├── storage/
│       │   │   │   └── s3_service.py
│       │   │   ├── ai/
│       │   │   │   └── claude_service.py
│       │   │   ├── external/
│       │   │   │   ├── weather_api.py
│       │   │   │   ├── mapbox_api.py
│       │   │   │   └── horoscope_api.py
│       │   │   ├── auth/
│       │   │   │   ├── jwt_handler.py
│       │   │   │   └── oauth_providers.py
│       │   │   └── notifications/
│       │   │       ├── fcm_service.py
│       │   │       └── email_service.py
│       │   │
│       │   └── presentation/
│       │       ├── api/
│       │       │   └── v1/
│       │       │       ├── auth.py
│       │       │       ├── users.py
│       │       │       ├── couples.py
│       │       │       ├── match.py
│       │       │       ├── events.py
│       │       │       ├── photos.py
│       │       │       ├── messages.py
│       │       │       ├── ari.py
│       │       │       ├── quests.py
│       │       │       ├── suggestions.py
│       │       │       ├── shared_space.py
│       │       │       └── settings.py
│       │       ├── websocket/
│       │       │   ├── chat_handler.py
│       │       │   └── notification_handler.py
│       │       ├── middleware/
│       │       │   ├── auth_middleware.py
│       │       │   ├── rate_limiter.py
│       │       │   └── cors.py
│       │       └── main.py           # FastAPI app entry
│       │
│       ├── migrations/               # Alembic migrations
│       ├── tests/
│       ├── alembic.ini
│       ├── pyproject.toml
│       └── Dockerfile
│
├── packages/
│   ├── ui/                           # Shared UI components (React)
│   │   ├── src/
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── modal.tsx
│   │   │   ├── avatar.tsx
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── shared/                       # Shared types & utils
│   │   ├── src/
│   │   │   ├── types/
│   │   │   ├── constants/
│   │   │   └── utils/
│   │   └── package.json
│   │
│   └── config/                       # Shared configs
│       ├── eslint/
│       ├── tailwind/
│       │   └── preset.ts             # Design system tokens
│       ├── typescript/
│       └── package.json
│
├── infra/
│   ├── docker/
│   │   ├── Dockerfile.web
│   │   ├── Dockerfile.api
│   │   └── docker-compose.yml        # PostgreSQL, Redis, MinIO (local S3)
│   ├── nginx/
│   └── scripts/
│       ├── seed.py                   # Seed database with sample data
│       └── setup-local.sh            # Local dev setup script
│
├── docs/
│   └── plan/
│
├── turbo.json
├── package.json
├── pyproject.toml
├── .env.example
├── .gitignore
└── CLAUDE.md
```

## 3. Data Flow Patterns

### Authentication Flow

```
Client → POST /api/v1/auth/login → Validate credentials →
Issue JWT (access: 15min) + Refresh Token (httpOnly cookie: 7d) →
Client stores access token in memory (Zustand) →
All subsequent requests: Authorization: Bearer <token>
```

### Photo Upload Flow (Presigned URL)

```
Client → POST /api/v1/photos/presign → Backend generates S3 presigned URL →
Client uploads directly to S3 → Client confirms: POST /api/v1/photos/confirm →
Backend saves metadata to PostgreSQL → Returns photo record
```

### Realtime Chat Flow

```
Client connects → WebSocket /ws/chat?token=<jwt> →
Backend authenticates → Joins couple's Redis channel →
Message sent → Backend saves to PostgreSQL → Publishes to Redis Pub/Sub →
Partner's WebSocket receives → Delivered
```

### AI Ari Chat Flow

```
Client → POST /api/v1/ari/chat → Use Case loads couple context →
Builds prompt with couple data (events, mood, days together) →
Calls Claude API (streaming) → Streams response back to client →
Saves conversation to DB
```

## 4. Key Technical Decisions

| Decision         | Choice                                     | Rationale                                         |
| ---------------- | ------------------------------------------ | ------------------------------------------------- |
| Monorepo tool    | Turborepo                                  | Fast, simple config, good Next.js integration     |
| Python framework | FastAPI                                    | Async-first, auto OpenAPI docs, fast performance  |
| ORM              | SQLAlchemy 2.0                             | Mature, async support, clean mapped_column syntax |
| Frontend state   | Zustand + TanStack Query                   | Zustand for UI state, TQ for server cache         |
| Auth tokens      | JWT in memory + Refresh in httpOnly cookie | Secure against XSS, CSRF protection               |
| File uploads     | S3 presigned URLs                          | No backend bottleneck, direct client→S3           |
| Realtime         | FastAPI WebSocket + Redis Pub/Sub          | Scalable, supports multiple backend instances     |
| AI               | Claude API direct                          | Best Vietnamese support, conversation context     |
| Image processing | S3 + Lambda/CloudFront Functions           | On-the-fly resize/WebP conversion                 |
| Task queue       | Celery + Redis                             | Background jobs: notifications, weekly reports    |

## 5. Infrastructure (Development)

### docker-compose.yml services:

- `postgres`: PostgreSQL 16 on port 5432
- `redis`: Redis 7 on port 6379
- `minio`: S3-compatible storage on port 9000 (local dev)
- `mailpit`: Email testing on port 1025/8025

### Environment Variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `AWS_S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `CLAUDE_API_KEY`: Anthropic API key for Ari
- `JWT_SECRET_KEY`: Secret for JWT signing
- `MAPBOX_TOKEN`: Mapbox GL access token
- `OPENWEATHER_API_KEY`: Weather data
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: OAuth
- `NEXT_PUBLIC_API_URL`: Backend API URL (`https://api-love.eraquix.com`)
- `NEXT_PUBLIC_WS_URL`: WebSocket URL (`wss://api-love.eraquix.com`)
- `NEXT_PUBLIC_MAPBOX_TOKEN`: Mapbox public token
- `NEXT_PUBLIC_APP_URL`: Frontend URL (`https://love.eraquix.com`)
