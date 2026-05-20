# Eralove - Database Schema Design

## Conventions
- All IDs: UUID v7 (time-sortable)
- All tables: `created_at TIMESTAMPTZ DEFAULT now()`, `updated_at TIMESTAMPTZ`
- Soft delete: `deleted_at TIMESTAMPTZ NULL`
- JSONB for flexible metadata

---

## Core Tables

### users
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),          -- NULL if social-only login
    display_name    VARCHAR(100) NOT NULL,
    username        VARCHAR(50) UNIQUE NOT NULL,
    avatar_url      TEXT,
    date_of_birth   DATE,
    gender          VARCHAR(20),
    zodiac_sign     VARCHAR(20),           -- auto-calculated from DOB
    love_language    VARCHAR(50),           -- from MBTI onboarding test
    bio             TEXT,
    is_email_verified BOOLEAN DEFAULT FALSE,
    is_onboarded    BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret  VARCHAR(255),
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### oauth_accounts
```sql
CREATE TABLE oauth_accounts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider    VARCHAR(20) NOT NULL,    -- google, apple, facebook
    provider_id VARCHAR(255) NOT NULL,
    email       VARCHAR(255),
    metadata    JSONB,
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(provider, provider_id)
);

CREATE INDEX idx_oauth_user ON oauth_accounts(user_id);
```

### refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL,
    device_info JSONB,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_refresh_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_expires ON refresh_tokens(expires_at);
```

---

## Couple & Match Tables

### couples
```sql
CREATE TABLE couples (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user1_id        UUID NOT NULL REFERENCES users(id),
    user2_id        UUID NOT NULL REFERENCES users(id),
    start_date      DATE NOT NULL,         -- ngay bat dau yeu
    couple_photo_url TEXT,
    status          VARCHAR(20) DEFAULT 'active', -- active, paused, broken_up
    theme_color     VARCHAR(20) DEFAULT 'rose',
    wallpaper_url   TEXT,
    nicknames       JSONB,                 -- {"user1": "Gau", "user2": "Meo"}
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    paused_at       TIMESTAMPTZ,
    broken_up_at    TIMESTAMPTZ,
    UNIQUE(user1_id, user2_id)
);

CREATE INDEX idx_couples_user1 ON couples(user1_id);
CREATE INDEX idx_couples_user2 ON couples(user2_id);
CREATE INDEX idx_couples_status ON couples(status);
```

### match_requests
```sql
CREATE TABLE match_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id       UUID NOT NULL REFERENCES users(id),
    receiver_id     UUID NOT NULL REFERENCES users(id),
    message         TEXT,
    status          VARCHAR(20) DEFAULT 'pending', -- pending, accepted, declined, expired
    proposed_start_date DATE,
    expires_at      TIMESTAMPTZ,           -- auto-expire after 7 days
    responded_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_match_sender ON match_requests(sender_id);
CREATE INDEX idx_match_receiver ON match_requests(receiver_id);
CREATE INDEX idx_match_status ON match_requests(status);
```

---

## Calendar & Events

### love_events
```sql
CREATE TABLE love_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id       UUID NOT NULL REFERENCES couples(id) ON DELETE CASCADE,
    created_by      UUID NOT NULL REFERENCES users(id),
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    event_type      VARCHAR(30) NOT NULL,  -- date, anniversary, travel, birthday, custom
    event_date      DATE NOT NULL,
    event_time      TIME,
    end_date        DATE,
    location_name   VARCHAR(255),
    latitude        DECIMAL(10, 7),
    longitude       DECIMAL(10, 7),
    color           VARCHAR(20),
    icon            VARCHAR(50),
    is_recurring    BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(100),          -- RRULE format
    reminder_before INTERVAL,              -- e.g., '1 day', '1 week'
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_events_couple ON love_events(couple_id);
CREATE INDEX idx_events_date ON love_events(event_date);
CREATE INDEX idx_events_type ON love_events(event_type);
CREATE INDEX idx_events_location ON love_events USING GIST (
    point(longitude, latitude)
) WHERE latitude IS NOT NULL;
```

### photos
```sql
CREATE TABLE photos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id       UUID NOT NULL REFERENCES couples(id) ON DELETE CASCADE,
    uploaded_by     UUID NOT NULL REFERENCES users(id),
    event_id        UUID REFERENCES love_events(id) ON DELETE SET NULL,
    s3_key          VARCHAR(500) NOT NULL,
    thumbnail_key   VARCHAR(500),
    original_url    TEXT NOT NULL,
    thumbnail_url   TEXT,
    caption         TEXT,
    photo_date      DATE,
    location_name   VARCHAR(255),
    latitude        DECIMAL(10, 7),
    longitude       DECIMAL(10, 7),
    width           INT,
    height          INT,
    file_size       BIGINT,
    mime_type       VARCHAR(50),
    exif_data       JSONB,
    created_at      TIMESTAMPTZ DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_photos_couple ON photos(couple_id);
CREATE INDEX idx_photos_event ON photos(event_id);
CREATE INDEX idx_photos_date ON photos(photo_date);
```

### time_capsules
```sql
CREATE TABLE time_capsules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id       UUID NOT NULL REFERENCES couples(id) ON DELETE CASCADE,
    created_by      UUID NOT NULL REFERENCES users(id),
    content_type    VARCHAR(20) NOT NULL,  -- text, photo, video
    content         TEXT,
    media_url       TEXT,
    unlock_at       TIMESTAMPTZ NOT NULL,
    is_opened       BOOLEAN DEFAULT FALSE,
    opened_at       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_capsules_couple ON time_capsules(couple_id);
CREATE INDEX idx_capsules_unlock ON time_capsules(unlock_at);
```

---

## Chat & Messaging

### messages
```sql
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id       UUID NOT NULL REFERENCES couples(id) ON DELETE CASCADE,
    sender_id       UUID NOT NULL REFERENCES users(id),
    content         TEXT,
    message_type    VARCHAR(20) DEFAULT 'text', -- text, image, video, voice, file, love_message, secret, draw
    media_url       TEXT,
    media_metadata  JSONB,                 -- {duration, size, dimensions}
    reply_to_id     UUID REFERENCES messages(id),
    is_pinned       BOOLEAN DEFAULT FALSE,
    is_secret       BOOLEAN DEFAULT FALSE, -- scratch-to-reveal
    is_revealed     BOOLEAN DEFAULT FALSE,
    status          VARCHAR(20) DEFAULT 'sent', -- sent, delivered, read
    delivered_at    TIMESTAMPTZ,
    read_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    deleted_for     UUID[]                 -- array of user IDs who deleted this
);

CREATE INDEX idx_messages_couple ON messages(couple_id);
CREATE INDEX idx_messages_created ON messages(couple_id, created_at DESC);
CREATE INDEX idx_messages_pinned ON messages(couple_id) WHERE is_pinned = TRUE;
```

### message_reactions
```sql
CREATE TABLE message_reactions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id  UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id),
    emoji       VARCHAR(10) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(message_id, user_id)
);
```

### call_logs
```sql
CREATE TABLE call_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    caller_id   UUID NOT NULL REFERENCES users(id),
    call_type   VARCHAR(10) NOT NULL,     -- voice, video
    status      VARCHAR(20) NOT NULL,     -- missed, answered, declined
    started_at  TIMESTAMPTZ,
    ended_at    TIMESTAMPTZ,
    duration    INT,                       -- seconds
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_calls_couple ON call_logs(couple_id);
```

---

## AI Mascot Ari

### ari_conversations
```sql
CREATE TABLE ari_conversations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    user_id     UUID NOT NULL REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

### ari_messages
```sql
CREATE TABLE ari_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES ari_conversations(id) ON DELETE CASCADE,
    role            VARCHAR(10) NOT NULL,  -- user, assistant
    content         TEXT NOT NULL,
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_ari_messages_conv ON ari_messages(conversation_id, created_at);
```

### ari_pet_state
```sql
CREATE TABLE ari_pet_state (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id       UUID UNIQUE NOT NULL REFERENCES couples(id),
    happiness       INT DEFAULT 50 CHECK (happiness BETWEEN 0 AND 100),
    health          INT DEFAULT 100 CHECK (health BETWEEN 0 AND 100),
    accessories     JSONB DEFAULT '[]',    -- ["hat_santa", "glasses_heart"]
    last_fed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ
);
```

---

## Gamification

### daily_quizzes
```sql
CREATE TABLE daily_quizzes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question    TEXT NOT NULL,
    category    VARCHAR(50),               -- memories, preferences, dreams, fun
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

### quiz_answers
```sql
CREATE TABLE quiz_answers (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id     UUID NOT NULL REFERENCES daily_quizzes(id),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    user_id     UUID NOT NULL REFERENCES users(id),
    answer      TEXT NOT NULL,
    quiz_date   DATE NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(quiz_id, couple_id, user_id, quiz_date)
);

CREATE INDEX idx_quiz_answers_couple ON quiz_answers(couple_id, quiz_date);
```

### love_quests
```sql
CREATE TABLE love_quests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    quest_type      VARCHAR(20) NOT NULL,  -- daily, weekly, special
    difficulty      VARCHAR(10),           -- easy, medium, hard
    coins_reward    INT DEFAULT 10,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

### couple_quests
```sql
CREATE TABLE couple_quests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id       UUID NOT NULL REFERENCES couples(id),
    quest_id        UUID NOT NULL REFERENCES love_quests(id),
    status          VARCHAR(20) DEFAULT 'in_progress', -- in_progress, completed, expired
    assigned_at     TIMESTAMPTZ DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ
);

CREATE INDEX idx_couple_quests ON couple_quests(couple_id, status);
```

### love_coins
```sql
CREATE TABLE love_coins (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    balance     INT DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ,
    UNIQUE(couple_id)
);
```

### coin_transactions
```sql
CREATE TABLE coin_transactions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    amount      INT NOT NULL,             -- positive = earned, negative = spent
    reason      VARCHAR(100) NOT NULL,    -- quiz_completed, quest_done, buy_accessory
    metadata    JSONB,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_coin_tx_couple ON coin_transactions(couple_id);
```

---

## Shared Space

### shared_notes
```sql
CREATE TABLE shared_notes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    created_by  UUID NOT NULL REFERENCES users(id),
    title       VARCHAR(255) NOT NULL,
    content     TEXT,
    category    VARCHAR(50),              -- general, important, partner_info
    is_pinned   BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ,
    deleted_at  TIMESTAMPTZ
);
```

### shared_todos
```sql
CREATE TABLE shared_todos (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    created_by  UUID NOT NULL REFERENCES users(id),
    list_type   VARCHAR(30) NOT NULL,     -- grocery, travel_packing, custom
    list_name   VARCHAR(255) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ
);
```

### shared_todo_items
```sql
CREATE TABLE shared_todo_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    list_id     UUID NOT NULL REFERENCES shared_todos(id) ON DELETE CASCADE,
    title       VARCHAR(255) NOT NULL,
    is_done     BOOLEAN DEFAULT FALSE,
    done_by     UUID REFERENCES users(id),
    sort_order  INT DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

### date_fund_transactions
```sql
CREATE TABLE date_fund_transactions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    paid_by     UUID NOT NULL REFERENCES users(id),
    amount      DECIMAL(12, 2) NOT NULL,
    currency    VARCHAR(3) DEFAULT 'VND',
    category    VARCHAR(50),              -- food, movie, travel, gift, other
    description VARCHAR(255),
    transaction_date DATE NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_fund_couple ON date_fund_transactions(couple_id);
CREATE INDEX idx_fund_date ON date_fund_transactions(transaction_date);
```

---

## Mood & Daily Check-in

### mood_checkins
```sql
CREATE TABLE mood_checkins (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    couple_id   UUID NOT NULL REFERENCES couples(id),
    user_id     UUID NOT NULL REFERENCES users(id),
    mood_emoji  VARCHAR(10) NOT NULL,
    mood_note   TEXT,
    checkin_date DATE NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(couple_id, user_id, checkin_date)
);

CREATE INDEX idx_mood_couple ON mood_checkins(couple_id, checkin_date);
```

---

## Notifications

### notifications
```sql
CREATE TABLE notifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    type        VARCHAR(50) NOT NULL,     -- match_request, message, event_reminder, quiz, quest, ari
    title       VARCHAR(255) NOT NULL,
    body        TEXT,
    data        JSONB,                    -- deep link info, related entity IDs
    is_read     BOOLEAN DEFAULT FALSE,
    read_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id) WHERE is_read = FALSE;
```

### push_tokens
```sql
CREATE TABLE push_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    token       TEXT NOT NULL,
    platform    VARCHAR(10) NOT NULL,     -- web, ios, android
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, token)
);
```

---

## Settings

### user_settings
```sql
CREATE TABLE user_settings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE NOT NULL REFERENCES users(id),
    theme               VARCHAR(10) DEFAULT 'light',   -- light, dark, auto
    primary_color       VARCHAR(20) DEFAULT 'rose',
    font_style          VARCHAR(20) DEFAULT 'rounded',
    notification_enabled BOOLEAN DEFAULT TRUE,
    quiet_hours_start   TIME,
    quiet_hours_end     TIME,
    notification_sound  VARCHAR(50) DEFAULT 'default',
    share_location      BOOLEAN DEFAULT FALSE,
    language            VARCHAR(5) DEFAULT 'vi',
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ
);
```

### login_history
```sql
CREATE TABLE login_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    ip_address  INET,
    user_agent  TEXT,
    device_info JSONB,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_login_user ON login_history(user_id, created_at DESC);
```

---

## Redis Data Structures

| Key Pattern | Type | TTL | Purpose |
|---|---|---|---|
| `session:{user_id}` | Hash | 24h | Active session data |
| `couple:{couple_id}:online` | Set | - | Online user IDs in couple |
| `chat:{couple_id}:typing` | String | 5s | Typing indicator |
| `weather:{lat}:{lon}` | Hash | 1h | Cached weather data |
| `horoscope:{sign}:{date}` | String | 24h | Daily horoscope cache |
| `daily_quote:{date}` | String | 24h | Daily love quote |
| `rate_limit:{user_id}:{endpoint}` | Counter | 1min | API rate limiting |
| `ws:connections:{user_id}` | String | - | WebSocket connection mapping |
| `couple:{couple_id}:unread:{user_id}` | Counter | - | Unread message count |
