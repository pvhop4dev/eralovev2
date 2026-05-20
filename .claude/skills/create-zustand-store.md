---
name: create-zustand-store
description: Create a new Zustand store for client-side state management
---

# Create Zustand Store

When asked to manage client-side state, follow this pattern:

## 1. Create the Store

```typescript
// apps/web/src/stores/{domain}-store.ts
import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";

// 1. Define types
interface {Domain}State {
  // State
  items: {Item}[];
  selectedId: string | null;
  isLoading: boolean;
  filters: {
    search: string;
    category: string;
  };

  // Actions
  setItems: (items: {Item}[]) => void;
  addItem: (item: {Item}) => void;
  removeItem: (id: string) => void;
  selectItem: (id: string | null) => void;
  setFilter: (key: keyof {Domain}State["filters"], value: string) => void;
  reset: () => void;
}

// 2. Define initial state
const initialState = {
  items: [],
  selectedId: null,
  isLoading: false,
  filters: {
    search: "",
    category: "all",
  },
};

// 3. Create store
export const use{Domain}Store = create<{Domain}State>()(
  devtools(
    immer((set) => ({
      ...initialState,

      setItems: (items) =>
        set((state) => {
          state.items = items;
        }),

      addItem: (item) =>
        set((state) => {
          state.items.push(item);
        }),

      removeItem: (id) =>
        set((state) => {
          state.items = state.items.filter((i) => i.id !== id);
        }),

      selectItem: (id) =>
        set((state) => {
          state.selectedId = id;
        }),

      setFilter: (key, value) =>
        set((state) => {
          state.filters[key] = value;
        }),

      reset: () => set(initialState),
    })),
    { name: "{domain}-store" },
  ),
);
```

## 2. With Persistence (localStorage)

Only for data that should survive page refreshes:

```typescript
export const useThemeStore = create<ThemeState>()(
  devtools(
    persist(
      (set) => ({
        theme: "system",
        accentColor: "#FF6B9D",
        setTheme: (theme) => set({ theme }),
        setAccentColor: (color) => set({ accentColor: color }),
      }),
      {
        name: "eralove-theme",  // localStorage key
        partialize: (state) => ({
          theme: state.theme,
          accentColor: state.accentColor,
        }),
      },
    ),
    { name: "theme-store" },
  ),
);
```

## 3. Computed/Derived Values (Selectors)

```typescript
// Selectors — define outside component to prevent re-renders
export const useFilteredItems = () =>
  use{Domain}Store((state) => {
    const { items, filters } = state;
    return items.filter((item) => {
      if (filters.search && !item.title.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      if (filters.category !== "all" && item.category !== filters.category) {
        return false;
      }
      return true;
    });
  });

export const useSelectedItem = () =>
  use{Domain}Store((state) =>
    state.items.find((i) => i.id === state.selectedId) ?? null,
  );

export const useItemCount = () =>
  use{Domain}Store((state) => state.items.length);
```

## 4. Usage in Components

```tsx
"use client";

import { use{Domain}Store, useFilteredItems } from "@/stores/{domain}-store";

export function {Domain}List() {
  // Use selectors for specific slices (prevents unnecessary re-renders)
  const items = useFilteredItems();
  const selectItem = use{Domain}Store((s) => s.selectItem);
  const setFilter = use{Domain}Store((s) => s.setFilter);

  return (
    <div>
      <input
        onChange={(e) => setFilter("search", e.target.value)}
        placeholder="Tìm kiếm..."
      />
      {items.map((item) => (
        <div key={item.id} onClick={() => selectItem(item.id)}>
          {item.title}
        </div>
      ))}
    </div>
  );
}
```

## When to Use What

| State Type | Solution | Example |
|---|---|---|
| Server data (API responses) | TanStack Query | Events, messages, user profile |
| UI state (modals, selections) | Zustand | Selected tab, sidebar open, modal state |
| Form state | React Hook Form | Create event form, settings form |
| Auth state | Zustand (persist) | User session, access token |
| Theme/preferences | Zustand (persist) | Dark mode, accent color, language |
| Real-time data | Zustand + Socket.IO | Online status, typing indicator |
| URL state | Next.js searchParams | Filters, pagination, sort |

## Eralove Stores

```
stores/
├── auth-store.ts          # User, tokens, login/logout
├── theme-store.ts         # Theme, accent color, font (persisted)
├── chat-store.ts          # Active chat state, typing, draft message
├── notification-store.ts  # Unread count, notification list
├── couple-store.ts        # Partner info, couple data, online status
├── ui-store.ts            # Sidebar, modals, sheets, tooltips
└── ari-store.ts           # Mascot state, mood, coins
```

## Rules
- **NEVER** store server data in Zustand — use TanStack Query
- **ALWAYS** use selectors to prevent unnecessary re-renders
- **ALWAYS** use `immer` middleware for complex state updates
- **ONLY** use `persist` for user preferences, not for API data
- Use `devtools` middleware in development for debugging
- Keep stores small and focused (one per domain)
- Define selectors outside components
