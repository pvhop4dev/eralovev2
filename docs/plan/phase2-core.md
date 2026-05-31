# Eralove - Phase 2: Core Features Implementation Plan

## Goal

Full Calendar experience, Love Map, AI Mascot Ari, Gamification (Quiz & Quests), OS Widgets.

## Timeline: Month 4-6 (6 sprints)

---

## Sprint 8: Calendar Header Widget (Week 15-16)

### Tasks

- [ ] Backend: Weather API integration (OpenWeatherMap) — cache in Redis 1h
- [ ] Backend: Horoscope service (12 zodiac signs daily) — cache in Redis 24h
- [ ] Backend: Feng shui / lunar calendar calculation (Python `lunardate` lib)
- [ ] Backend: `GET /dashboard/header-widget` aggregated endpoint
- [ ] Frontend: Header widget UI above calendar
  - Today's date (Vietnamese format) + lunar date
  - Weather (temp, icon, location)
  - Love quote of the day
  - Days together counter
  - Zodiac for both users
  - Feng shui (good/bad day, lucky color, lucky direction)
- [ ] Frontend: Calendar year view
- [ ] Frontend: Event search & filter

---

## Sprint 9: Love Map (Week 17-18)

### Tasks

- [ ] Backend: Location aggregation endpoints
- [ ] Backend: Heatmap data generation
- [ ] Backend: Journey (chronological waypoints)
- [ ] Backend: Travel statistics (cities, km)
- [ ] Backend: Travel badges logic
- [ ] Frontend: Mapbox GL JS integration with romantic pastel style
- [ ] Frontend: Event/photo pins (heart markers, color by type)
- [ ] Frontend: Pin click → popup (thumbnail + title + date)
- [ ] Frontend: Cluster pins on zoom out
- [ ] Frontend: Heatmap layer toggle
- [ ] Frontend: "Our Journey" mode — animated line connecting locations
- [ ] Frontend: Filter by event type, date range, has photos
- [ ] Frontend: Statistics panel (cities, km, badges)
- [ ] Frontend: Live location sharing toggle (optional)

---

## Sprint 10: Mascot Ari — AI Chatbot (Week 19-20)

### Tasks

- [ ] Backend: Claude API integration service
- [ ] Backend: Ari system prompt engineering
  - Personality: cute pink-purple cat, warm, non-judgmental
  - Context: couple's start date, events, mood history, love language
  - Topics: conflict resolution, date ideas, apology help, emotional support
- [ ] Backend: Ari conversation management (create, continue, list)
- [ ] Backend: Streaming response (SSE)
- [ ] Backend: Daily check-in Ari question generation
- [ ] Backend: Weekly love report generation (message count, events, mood trends)
- [ ] Frontend: Ari chat interface (distinct from couple chat)
  - Ari avatar (animated cat)
  - Chat bubbles with Ari personality
  - Streaming text display
  - Suggested quick replies
- [ ] Frontend: Daily check-in modal (Ari asks, user picks emoji + note)
- [ ] Frontend: Weekly report card (stats + Ari advice)

---

## Sprint 11: Ari Virtual Pet (Week 21-22)

### Tasks

- [ ] Backend: Pet state management (happiness, health)
  - Happiness increases: send messages, add events, do quests
  - Happiness decreases: low interaction days
  - Health decreases: couple arguments detected (sentiment)
- [ ] Backend: Accessory shop (list, buy with love coins)
- [ ] Backend: AI sentiment analysis on chat messages
  - Detect negative tone → trigger Ari warning popup
- [ ] Frontend: Ari pet display on dashboard
  - Animated cat (idle, happy, sad, sleeping)
  - Happiness/health bars
  - Equipped accessories displayed on Ari
- [ ] Frontend: Accessory shop UI
  - Grid of accessories (hats, glasses, bow ties)
  - Buy with love coins
  - Equip/unequip
- [ ] Frontend: Ari sentiment warning popup
  - "You both seem upset. Take a deep breath together!"
- [ ] Frontend: Gyroscope interaction (tilt phone, Ari slides)

---

## Sprint 12: Daily Quiz & Weekly Quests (Week 23-24)

### Tasks

- [ ] Backend: Quiz system
  - Seed 200+ questions (memories, preferences, dreams, fun)
  - Daily quiz selection (never repeat for same couple in 30 days)
  - Answer submission — hidden until both answer
  - Love coins reward for participation
- [ ] Backend: Quest system
  - Seed 50+ quests (daily, weekly, special)
  - Quest assignment logic (weekly rotation)
  - Completion verification
  - Love coins reward
- [ ] Backend: Love coins ledger (earn/spend, balance)
- [ ] Frontend: Daily Quiz card on dashboard
  - Question display
  - Text answer input
  - "Waiting for partner" state
  - Reveal animation (both answers side by side)
  - Coins earned celebration
- [ ] Frontend: Quest board
  - Active quests list
  - Quest detail (description, difficulty, reward)
  - Complete button with optional proof photo
  - Completed quest history
- [ ] Frontend: Love coins display & transaction history

---

## Sprint 13: Time Capsule & Polish (Week 25-26)

### Tasks

- [ ] Backend: Time capsule CRUD
- [ ] Backend: Time capsule unlock scheduler (check daily, send notification)
- [ ] Frontend: Create time capsule (text, photo, video)
  - Pick unlock date (datepicker)
  - Preview before sealing
- [ ] Frontend: Time capsule list
  - Locked capsules: gift box with countdown
  - Unlocked capsules: open and view content
  - Opening animation (unwrap gift)
- [ ] Backend: Voice & Video call signaling (WebRTC)
- [ ] Frontend: Voice call UI (basic)
- [ ] Frontend: Video call UI (basic)
- [ ] Phase 2 testing & bug fixes
- [ ] Performance optimization
- [ ] Cross-browser testing

---

## Phase 2 Feature Summary

| Feature                                                | Sprint    |
| ------------------------------------------------------ | --------- |
| Calendar Header Widget (weather, horoscope, feng shui) | Sprint 8  |
| Calendar Year View & Search                            | Sprint 8  |
| Love Map (Mapbox, pins, heatmap, journey)              | Sprint 9  |
| Live Location Sharing                                  | Sprint 9  |
| Travel Statistics & Badges                             | Sprint 9  |
| AI Ari Chatbot (Claude API)                            | Sprint 10 |
| Ari Daily Check-in                                     | Sprint 10 |
| Ari Weekly Love Report                                 | Sprint 10 |
| Ari Virtual Pet                                        | Sprint 11 |
| AI Sentiment Analysis                                  | Sprint 11 |
| Accessory Shop                                         | Sprint 11 |
| Daily Love Quiz                                        | Sprint 12 |
| Weekly Love Quests                                     | Sprint 12 |
| Love Coins System                                      | Sprint 12 |
| Time Capsule                                           | Sprint 13 |
| Voice & Video Call (basic)                             | Sprint 13 |
