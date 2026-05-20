# Eralove - API Design

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://api-love.eraquix.com/api/v1`
- WebSocket Dev: `ws://localhost:8000/ws`
- WebSocket Prod: `wss://api-love.eraquix.com/ws`
- Frontend: `https://love.eraquix.com`

## Response Format
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "cursor": "next_cursor_token"
  },
  "error": null
}
```

## Error Format
```json
{
  "data": null,
  "meta": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is already registered",
    "details": [...]
  }
}
```

---

## Auth Endpoints

### POST /auth/register
Register a new user.
```
Body: { email, password, display_name, date_of_birth, gender }
→ 201: { user, access_token } + Set-Cookie: refresh_token
```

### POST /auth/login
Login with email/password.
```
Body: { email, password }
→ 200: { user, access_token } + Set-Cookie: refresh_token
```

### POST /auth/oauth
Login with OAuth provider.
```
Body: { provider: "google"|"apple"|"facebook", token }
→ 200: { user, access_token, is_new_user }
```

### POST /auth/refresh
Refresh access token.
```
Cookie: refresh_token
→ 200: { access_token }
```

### POST /auth/logout
Invalidate refresh token.
```
→ 204
```

### POST /auth/forgot-password
Send password reset email.
```
Body: { email }
→ 200: { message }
```

### POST /auth/verify-email
Verify email with OTP.
```
Body: { email, otp }
→ 200: { verified: true }
```

---

## User Endpoints

### GET /users/me
Get current user profile.
```
→ 200: { user }
```

### PATCH /users/me
Update current user profile.
```
Body: { display_name?, avatar_url?, bio?, ... }
→ 200: { user }
```

### GET /users/search?q={query}
Search users by username or email (for match).
```
→ 200: { users: [{ id, username, display_name, avatar_url }] }
```

### POST /users/me/onboarding
Complete onboarding.
```
Body: { display_name, avatar_url, date_of_birth, love_language, wallpaper }
→ 200: { user }
```

---

## Match Endpoints

### POST /match/request
Send a match request.
```
Body: { receiver_id, message?, proposed_start_date? }
→ 201: { match_request }
```

### GET /match/requests
Get pending match requests (sent & received).
```
→ 200: { sent: [...], received: [...] }
```

### POST /match/requests/{id}/accept
Accept a match request.
```
Body: { start_date }
→ 200: { couple }
```

### POST /match/requests/{id}/decline
Decline a match request.
```
Body: { reason? }
→ 200: { match_request }
```

### POST /match/unmatch
Unmatch from current partner.
```
Body: { confirmation_code }
→ 200: { message }
```

---

## Couple Endpoints

### GET /couple
Get current couple info.
```
→ 200: { couple, partner, days_together, love_coins }
```

### PATCH /couple
Update couple settings.
```
Body: { couple_photo_url?, theme_color?, wallpaper_url?, nicknames? }
→ 200: { couple }
```

### POST /couple/pause
Pause the relationship (breakup mode).
```
→ 200: { couple }
```

### POST /couple/resume
Request to resume the relationship.
```
→ 200: { message }
```

---

## Calendar / Events Endpoints

### GET /events?month={YYYY-MM}&type={type}
Get events for a month.
```
→ 200: { events: [...] }
```

### POST /events
Create a new event.
```
Body: {
  title, description?, event_type, event_date, event_time?,
  location_name?, latitude?, longitude?, color?, icon?,
  is_recurring?, recurrence_rule?, reminder_before?
}
→ 201: { event }
```

### GET /events/{id}
Get event details with photos.
```
→ 200: { event, photos: [...] }
```

### PATCH /events/{id}
Update an event.
```
Body: { ...partial event fields }
→ 200: { event }
```

### DELETE /events/{id}
Soft delete an event.
```
→ 204
```

### POST /events/{id}/restore
Restore a deleted event (within 30 days).
```
→ 200: { event }
```

---

## Photo Endpoints

### POST /photos/presign
Get presigned URL for upload.
```
Body: { filename, content_type, event_id? }
→ 200: { upload_url, s3_key, expires_in }
```

### POST /photos/confirm
Confirm upload and save metadata.
```
Body: { s3_key, event_id?, caption?, photo_date?, location_name?, latitude?, longitude? }
→ 201: { photo }
```

### GET /photos?page={n}&event_id={id}&date_from={}&date_to={}
Get photos with filters.
```
→ 200: { photos: [...], meta }
```

### DELETE /photos/{id}
Delete a photo.
```
→ 204
```

### GET /photos/memory-book?year={YYYY}&month={MM}
Get auto-generated memory book.
```
→ 200: { photos: [...], stats }
```

---

## Chat Endpoints

### GET /messages?cursor={cursor}&limit={n}
Get messages (cursor-based pagination, newest first).
```
→ 200: { messages: [...], meta: { next_cursor } }
```

### POST /messages
Send a message (also broadcast via WebSocket).
```
Body: { content?, message_type, media_url?, reply_to_id?, is_secret? }
→ 201: { message }
```

### POST /messages/{id}/pin
Pin/unpin a message.
```
→ 200: { message }
```

### POST /messages/{id}/react
React to a message.
```
Body: { emoji }
→ 200: { reaction }
```

### DELETE /messages/{id}?for={me|both}
Delete a message.
```
→ 204
```

### POST /messages/{id}/reveal
Reveal a secret message (scratch-to-reveal).
```
→ 200: { message }
```

### GET /messages/pinned
Get all pinned messages.
```
→ 200: { messages: [...] }
```

---

## AI Ari Endpoints

### POST /ari/chat
Chat with Ari (streaming response).
```
Body: { message, conversation_id? }
→ 200 (SSE stream): { conversation_id, content_chunk }
```

### GET /ari/conversations
Get Ari conversation history.
```
→ 200: { conversations: [...] }
```

### GET /ari/conversations/{id}/messages
Get messages in an Ari conversation.
```
→ 200: { messages: [...] }
```

### POST /ari/daily-checkin
Submit daily mood check-in.
```
Body: { mood_emoji, mood_note? }
→ 200: { checkin, ari_response }
```

### GET /ari/weekly-report
Get Ari's weekly love report.
```
→ 200: { report: { messages_count, events_count, mood_summary, advice } }
```

### GET /ari/pet
Get Ari pet state.
```
→ 200: { happiness, health, accessories }
```

### POST /ari/pet/accessory
Buy accessory with love coins.
```
Body: { accessory_id }
→ 200: { pet_state, coins_remaining }
```

---

## Quest & Quiz Endpoints

### GET /quests/daily-quiz
Get today's daily quiz.
```
→ 200: { quiz, my_answer?, partner_answered: bool }
```

### POST /quests/daily-quiz/{id}/answer
Submit daily quiz answer.
```
Body: { answer }
→ 200: { my_answer, partner_answer? (null if not answered yet), coins_earned? }
```

### GET /quests/current
Get current active quests.
```
→ 200: { quests: [...] }
```

### POST /quests/{id}/complete
Mark quest as completed.
```
Body: { proof_photo_url? }
→ 200: { quest, coins_earned }
```

---

## Love Map Endpoints

### GET /map/locations
Get all locations with events/photos.
```
→ 200: { locations: [{ lat, lng, event_count, photo_count, latest_event }] }
```

### GET /map/heatmap
Get heatmap data.
```
→ 200: { points: [{ lat, lng, weight }] }
```

### GET /map/journey
Get chronological journey line.
```
→ 200: { waypoints: [{ lat, lng, date, title }] }
```

### GET /map/stats
Get love map statistics.
```
→ 200: { cities_count, total_km, badges: [...] }
```

---

## Shared Space Endpoints

### GET /shared/notes
### POST /shared/notes
### PATCH /shared/notes/{id}
### DELETE /shared/notes/{id}

### GET /shared/todos
### POST /shared/todos
### POST /shared/todos/{id}/items
### PATCH /shared/todos/{id}/items/{item_id}
### DELETE /shared/todos/{id}

### GET /shared/fund?month={YYYY-MM}
### POST /shared/fund
### GET /shared/fund/stats
Get spending statistics.
```
→ 200: { total, by_user: {...}, by_category: {...}, monthly_chart: [...] }
```

---

## Time Capsule Endpoints

### POST /time-capsules
Create a time capsule.
```
Body: { content_type, content?, media_url?, unlock_at }
→ 201: { time_capsule }
```

### GET /time-capsules
Get all time capsules.
```
→ 200: { capsules: [...] }  (content hidden for locked ones)
```

### POST /time-capsules/{id}/open
Open a time capsule (only if unlock_at has passed).
```
→ 200: { time_capsule (with content) }
```

---

## Dashboard Endpoints

### GET /dashboard
Aggregated dashboard data.
```
→ 200: {
  couple, days_together, daily_quote, upcoming_events,
  memory_flashback, mood_today, current_quest, partner_status
}
```

### GET /dashboard/header-widget
Calendar header widget data.
```
→ 200: {
  date, lunar_date, weather, horoscope: { user1, user2 },
  feng_shui, love_quote, days_together
}
```

---

## Suggestion Endpoints

### GET /suggestions/gifts?budget={range}&occasion={type}
Get gift suggestions.
```
→ 200: { suggestions: [...] }
```

### GET /suggestions/dates?lat={}&lng={}&budget={}&category={}
Get date spot suggestions.
```
→ 200: { suggestions: [...] }
```

### GET /suggestions/anniversaries
Get upcoming anniversaries with suggestions.
```
→ 200: { anniversaries: [{ date, milestone, suggestions }] }
```

---

## Settings Endpoints

### GET /settings
### PATCH /settings
Update user settings.
```
Body: { theme?, primary_color?, notification_enabled?, quiet_hours_start?, ... }
→ 200: { settings }
```

### GET /settings/login-history
### POST /settings/change-password
### POST /settings/enable-2fa
### POST /settings/disable-2fa
### POST /settings/export-data
Request data export (background job).
```
→ 202: { export_id, status: "processing" }
```

### DELETE /settings/account
Delete account (requires password confirmation).
```
Body: { password }
→ 204
```

---

## Notification Endpoints

### GET /notifications?unread_only={bool}
### PATCH /notifications/{id}/read
### POST /notifications/read-all
### POST /notifications/push-token
Register push notification token.
```
Body: { token, platform }
→ 200
```

---

## WebSocket Events

### Connection
```
ws://localhost:8000/ws?token={jwt_access_token}
```

### Client → Server Events
| Event | Payload | Description |
|---|---|---|
| `message.send` | `{ content, type, reply_to_id? }` | Send chat message |
| `message.typing` | `{ is_typing: bool }` | Typing indicator |
| `message.read` | `{ message_id }` | Mark message as read |
| `love_touch` | `{}` | Send love touch vibration |
| `presence.status` | `{ status: "online"\|"away" }` | Update presence |

### Server → Client Events
| Event | Payload | Description |
|---|---|---|
| `message.new` | `{ message }` | New message received |
| `message.typing` | `{ user_id, is_typing }` | Partner typing |
| `message.status` | `{ message_id, status }` | Message delivered/read |
| `love_touch.received` | `{ from_user_id }` | Love touch received |
| `notification` | `{ notification }` | Push notification |
| `presence.update` | `{ user_id, status }` | Partner online/offline |
| `quiz.partner_answered` | `{ quiz_id }` | Partner answered quiz |
| `ari.state_changed` | `{ happiness, health }` | Ari pet state update |
