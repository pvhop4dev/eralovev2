---
name: create-redis-cache
description: Add Redis caching to an endpoint or service with proper key management and invalidation
---

# Add Redis Caching

When asked to add caching, follow this pattern:

## 1. Define Cache Key

```python
# Follow naming convention: eralove:{domain}:{identifier}:{sub-key}
CACHE_KEY = "eralove:{domain}:{id}:{scope}"
CACHE_TTL = 300  # seconds (5 minutes)
```

## 2. Add to Cache Service

```python
# apps/api/src/infrastructure/redis/cache.py
class CacheService:
    async def get_{domain}_{scope}(self, identifier: str) -> dict | None:
        key = f"eralove:{domain}:{identifier}:{scope}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_{domain}_{scope}(self, identifier: str, data: dict, ttl: int = CACHE_TTL) -> None:
        key = f"eralove:{domain}:{identifier}:{scope}"
        await self.redis.setex(key, ttl, json.dumps(data, default=str))

    async def invalidate_{domain}(self, identifier: str) -> None:
        """Invalidate all caches for this {domain}."""
        await self.invalidate_pattern(f"eralove:{domain}:{identifier}:*")
```

## 3. Use in Repository or Use Case

### Option A: Cache in Repository (for hot data)
```python
class CachedEventRepository(EventRepository):
    def __init__(self, db_repo: PostgresEventRepository, cache: CacheService):
        self.db_repo = db_repo
        self.cache = cache

    async def get_by_id(self, event_id: UUID) -> Event | None:
        # Try cache first
        cached = await self.cache.get_event_detail(str(event_id))
        if cached:
            return Event(**cached)

        # Cache miss — fetch from DB
        event = await self.db_repo.get_by_id(event_id)
        if event:
            await self.cache.set_event_detail(str(event_id), event.to_dict())
        return event
```

### Option B: Cache in Use Case (for computed/aggregated data)
```python
class GetDashboardUseCase:
    async def execute(self, user_id: UUID) -> DashboardResponse:
        couple = await self.couple_repo.get_by_user(user_id)
        cache_key = f"eralove:couple:{couple.id}:dashboard"

        return await self.cache.get_or_set(
            key=cache_key,
            factory=lambda: self._build_dashboard(couple),
            ttl=300,  # 5 minutes
        )

    async def _build_dashboard(self, couple: Couple) -> dict:
        events, photos, weather = await asyncio.gather(...)
        return {
            "days_together": couple.days_together(),
            "upcoming_events": [...],
            "recent_photos": [...],
            "weather": weather,
        }
```

## 4. Invalidate on Write

```python
class CreateEventUseCase:
    async def execute(self, dto, user_id):
        event = await self.event_repo.create(...)

        # Invalidate related caches
        await self.cache.invalidate(
            f"eralove:couple:{couple.id}:dashboard",
            f"eralove:couple:{couple.id}:events:{event.event_date.strftime('%Y-%m')}",
        )

        return EventResponse.model_validate(event)
```

## TTL Reference

| Data | TTL | Reason |
|---|---|---|
| Weather data | 1 hour | External API, rarely changes |
| Daily horoscope | 24 hours | Changes daily |
| Daily quote | 24 hours | Changes daily |
| Dashboard summary | 5 min | Frequently updated |
| User profile | 30 min | Rarely changes |
| Event details | 15 min | Occasional updates |
| Couple days count | 24 hours | Changes daily |
| Online status | 5 min | Heartbeat refreshed |

## Checklist
- [ ] Cache key follows naming convention: `eralove:{domain}:{id}:{scope}`
- [ ] TTL is appropriate for data freshness requirements
- [ ] Cache invalidated on every write operation
- [ ] Graceful degradation: if Redis is down, fall back to DB
- [ ] No sensitive data cached (passwords, tokens, private messages)
- [ ] Pattern invalidation used carefully (only couple-scoped, not global)
