---
name: caching-performance
description: Redis caching strategies, TTL policies, cache invalidation, and performance optimization
---

# Caching & Performance Rules

## Redis Caching Strategy

### Key Naming Convention
```
eralove:{domain}:{identifier}:{sub-key}
```

| Key Pattern | TTL | Description |
|---|---|---|
| `eralove:user:{user_id}:profile` | 30 min | User profile data |
| `eralove:couple:{couple_id}:dashboard` | 5 min | Dashboard summary |
| `eralove:couple:{couple_id}:days_count` | 24 hr | Days together count |
| `eralove:weather:{lat}:{lon}` | 1 hr | Weather data by location |
| `eralove:horoscope:{sign}:{date}` | 24 hr | Daily horoscope |
| `eralove:quote:daily:{date}` | 24 hr | Daily love quote |
| `eralove:session:{user_id}:online` | 5 min | Online status (refreshed by heartbeat) |
| `eralove:rate_limit:{ip}:{endpoint}` | 1 min | Rate limiter counter |

### Caching Patterns

#### Cache-Aside (Read-Through)
```python
# apps/api/src/infrastructure/redis/cache.py
import json
from redis.asyncio import Redis

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl: int = 300,
    ) -> T:
        """Get from cache, or compute and store."""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        value = await factory()
        await self.redis.setex(key, ttl, json.dumps(value, default=str))
        return value

    async def invalidate(self, *keys: str) -> None:
        """Delete one or more cache keys."""
        if keys:
            await self.redis.delete(*keys)

    async def invalidate_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern. Use sparingly."""
        keys = []
        async for key in self.redis.scan_iter(match=pattern, count=100):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)
```

#### Write-Through (Invalidate on Write)
```python
# In use case: invalidate cache when data changes
class UpdateEventUseCase:
    async def execute(self, event_id: UUID, dto: UpdateEventRequest, user_id: UUID):
        # ... update in database
        event = await self.event_repo.update(event_id, dto)

        # Invalidate related caches
        await self.cache.invalidate(
            f"eralove:couple:{couple_id}:dashboard",
            f"eralove:couple:{couple_id}:events:{event.event_date.month}",
        )

        return event
```

### Cache Invalidation Rules
- **Create**: Invalidate list/collection caches
- **Update**: Invalidate item cache + list caches
- **Delete**: Invalidate item cache + list caches
- **Match/Unmatch**: Invalidate all couple-scoped caches (`eralove:couple:{id}:*`)
- **NEVER** rely on TTL alone for mutable data — always invalidate on write

## Backend Performance

### Database
- Connection pooling: `pool_size=20`, `max_overflow=10`
- Use `selectinload()` for relationships to prevent N+1
- Partial indexes on `deleted_at IS NULL` for soft-delete tables
- Use `EXPLAIN ANALYZE` for slow queries (> 100ms)
- Batch inserts for bulk operations (photos, quiz answers)

### API Response
- Enable gzip/brotli compression via middleware
- Pagination: max 100 items per page
- Select only needed columns: `select(User.id, User.display_name)` not `select(User)`
- Use `asyncio.gather()` for parallel I/O in dashboard endpoints

## Frontend Performance

### Code Splitting
```tsx
// Dynamic import for heavy components
const MapView = dynamic(() => import("@/features/map"), { ssr: false });
const ChatView = dynamic(() => import("@/features/chat"), { ssr: false });
const EmojiPicker = dynamic(() => import("@/components/emoji-picker"), { ssr: false });
```

### Image Optimization
- Format: WebP (via next/image automatic)
- Lazy loading: `loading="lazy"` (default in next/image)
- Responsive: always set `sizes` prop
- Blur placeholder: generate blur hash on upload (backend)

### TanStack Query Cache
```typescript
// Stale time configuration per data type
const STALE_TIMES = {
  user: 30 * 60 * 1000,      // 30 min — user rarely changes
  events: 5 * 60 * 1000,     // 5 min — events change occasionally
  messages: 0,                // Always fresh — real-time via WebSocket
  weather: 60 * 60 * 1000,   // 1 hour
  horoscope: 24 * 60 * 60 * 1000, // 24 hours
};

// Usage
useQuery({
  queryKey: ["events", month],
  queryFn: () => eventsApi.list(month),
  staleTime: STALE_TIMES.events,
});
```

### Optimistic Updates
```typescript
// Optimistic update for instant UI feedback
const mutation = useMutation({
  mutationFn: (data: CreateEventDto) => eventsApi.create(data),
  onMutate: async (newEvent) => {
    await queryClient.cancelQueries({ queryKey: ["events"] });
    const previous = queryClient.getQueryData(["events"]);
    queryClient.setQueryData(["events"], (old: Event[]) => [
      ...old,
      { ...newEvent, id: "temp", created_at: new Date().toISOString() },
    ]);
    return { previous };
  },
  onError: (err, _, context) => {
    queryClient.setQueryData(["events"], context?.previous);
    toast.error("Không thể tạo sự kiện");
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ["events"] });
  },
});
```

## Rules Summary

### MUST
- Cache all external API responses (weather, horoscope, quotes)
- Invalidate cache on every write operation
- Use connection pooling for database
- Use `next/image` with proper `sizes` for all images
- Use dynamic imports for Mapbox, Socket.IO, and heavy components

### MUST NOT
- Never cache authentication/authorization data in Redis (use JWT)
- Never use `KEYS *` in production Redis (use `SCAN`)
- Never fetch all records without pagination
- Never load full-resolution images without responsive `sizes`

### SHOULD
- Implement optimistic updates for all mutations in TanStack Query
- Use `Suspense` boundaries for parallel data loading
- Monitor cache hit rates and adjust TTLs accordingly
- Use `staleTime` appropriately per data type
