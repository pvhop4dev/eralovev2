---
name: frontend-patterns
description: Frontend coding patterns and conventions for Next.js app
---

# Frontend Patterns

## Server vs Client Components

### Default: Server Components
- Pages, layouts, data-fetching wrappers
- No `"use client"` directive needed

### Client Components (use `"use client"`)
- Interactive UI (buttons, forms, modals)
- Browser APIs (localStorage, geolocation)
- Hooks (useState, useEffect, custom hooks)
- Event handlers (onClick, onChange)
- Third-party client libraries (Framer Motion, Mapbox)

## Data Fetching

### Server-side (in Server Components)
```tsx
// app/(main)/events/page.tsx
async function EventsPage() {
  const events = await fetchEvents(); // direct API call
  return <EventList events={events} />;
}
```

### Client-side (TanStack Query)
```tsx
// features/calendar/hooks/use-events.ts
export function useEvents(month: string) {
  return useQuery({
    queryKey: ["events", month],
    queryFn: () => apiClient.get(`/events?month=${month}`),
  });
}
```

## API Client Pattern
```tsx
// lib/api-client.ts
// Single instance, handles auth token injection, refresh, error formatting
// All API calls MUST go through this client
import { apiClient } from "@/lib/api-client";

// In feature API files:
export const eventsApi = {
  list: (month: string) => apiClient.get<Event[]>(`/events?month=${month}`),
  create: (data: CreateEventDto) => apiClient.post<Event>("/events", data),
  update: (id: string, data: UpdateEventDto) => apiClient.patch<Event>(`/events/${id}`, data),
  delete: (id: string) => apiClient.delete(`/events/${id}`),
};
```

## State Management

### Zustand (UI/Client State)
```tsx
// stores/auth-store.ts
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  setAuth: (user, token) => set({ user, accessToken: token }),
  logout: () => set({ user: null, accessToken: null }),
}));
```

### TanStack Query (Server State)
- Use for all API data
- Configure staleTime per query type
- Use optimistic updates for mutations

## Component Pattern
- Props interface always defined
- Use `cn()` for conditional classes (clsx + twMerge)
- Spread remaining props with `...props`
- Forward ref when needed for form components

## Error Handling
- API errors caught by API client interceptor
- Toast notifications for user-facing errors
- Error boundaries for component crashes
- Loading skeletons for async content

## File Organization per Feature
```
features/calendar/
├── components/
│   ├── calendar-view.tsx
│   ├── event-card.tsx
│   └── event-form.tsx
├── hooks/
│   ├── use-events.ts
│   └── use-create-event.ts
├── api.ts          # API functions
└── types.ts        # Feature-specific types
```
