---
name: create-nextjs-page
description: Create a new Next.js 15 App Router page with proper layout, metadata, loading, and error states
---

# Create Next.js Page

When asked to create a new page/route, follow this pattern:

## 1. Create the Page

### Server Component Page (Default — data fetching)

```tsx
// apps/web/src/app/(main)/{feature}/page.tsx
import { Suspense } from "react";
import type { Metadata } from "next";
import { {Feature}View } from "@/features/{feature}/components/{feature}-view";
import { {Feature}Skeleton } from "@/features/{feature}/components/{feature}-skeleton";

export const metadata: Metadata = {
  title: "{Feature Title}",  // Template: "{Feature Title} | Eralove"
  description: "{Vietnamese description of this page}",
};

export default function {Feature}Page() {
  return (
    <div className="p-4 md:p-6 lg:p-8 space-y-6">
      <header>
        <h1 className="text-2xl font-heading font-bold text-purple-900 dark:text-pink-100">
          {emoji} {Feature Title}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          {Vietnamese subtitle}
        </p>
      </header>

      <Suspense fallback={<{Feature}Skeleton />}>
        <{Feature}View />
      </Suspense>
    </div>
  );
}
```

### Client Component Page (Interactive — WebSocket, real-time)

```tsx
// apps/web/src/app/(main)/{feature}/page.tsx
"use client";

import { {Feature}View } from "@/features/{feature}/components/{feature}-view";

export default function {Feature}Page() {
  return <{Feature}View />;
}
```

## 2. Create Loading State

```tsx
// apps/web/src/app/(main)/{feature}/loading.tsx
import { {Feature}Skeleton } from "@/features/{feature}/components/{feature}-skeleton";

export default function {Feature}Loading() {
  return <{Feature}Skeleton />;
}
```

## 3. Create Error State

```tsx
// apps/web/src/app/(main)/{feature}/error.tsx
"use client";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function {Feature}Error({ error, reset }: ErrorProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="w-16 h-16 rounded-full bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center mb-4">
        <span className="text-2xl">😢</span>
      </div>
      <h2 className="text-xl font-heading font-semibold text-purple-900 dark:text-pink-100">
        Đã xảy ra lỗi
      </h2>
      <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
        {error.message || "Có gì đó không ổn, hãy thử lại nhé."}
      </p>
      <button
        onClick={reset}
        className="mt-6 px-6 py-2.5 bg-rose-500 hover:bg-rose-600 text-white rounded-full font-medium transition-colors"
      >
        Thử lại
      </button>
    </div>
  );
}
```

## 4. Create Feature Module

### Components

```tsx
// apps/web/src/features/{feature}/components/{feature}-view.tsx
"use client";

import { use{Feature}s } from "../hooks/use-{feature}s";
import { {Feature}Card } from "./{feature}-card";

export function {Feature}View() {
  const { data, isLoading, error } = use{Feature}s();

  if (isLoading) return <{Feature}Skeleton />;
  if (error) return <ErrorState error={error} />;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data?.map((item) => (
        <{Feature}Card key={item.id} item={item} />
      ))}
    </div>
  );
}
```

### API Functions

```typescript
// apps/web/src/features/{feature}/api.ts
import { apiClient } from "@/lib/api-client";
import type { {Feature}, Create{Feature}Dto } from "./types";

export const {feature}sApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<{Feature}[]>("/api/v1/{feature}s", { params }),
  getById: (id: string) =>
    apiClient.get<{Feature}>(`/api/v1/{feature}s/${id}`),
  create: (data: Create{Feature}Dto) =>
    apiClient.post<{Feature}>("/api/v1/{feature}s", data),
  update: (id: string, data: Partial<Create{Feature}Dto>) =>
    apiClient.patch<{Feature}>(`/api/v1/{feature}s/${id}`, data),
  delete: (id: string) =>
    apiClient.delete(`/api/v1/{feature}s/${id}`),
};
```

### Hooks

```typescript
// apps/web/src/features/{feature}/hooks/use-{feature}s.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { {feature}sApi } from "../api";
import { toast } from "sonner";

export function use{Feature}s(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["{feature}s", params],
    queryFn: () => {feature}sApi.list(params),
  });
}

export function useCreate{Feature}() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: {feature}sApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["{feature}s"] });
      toast.success("Tạo thành công! 🎉");
    },
    onError: () => {
      toast.error("Không thể tạo, hãy thử lại.");
    },
  });
}
```

### Types

```typescript
// apps/web/src/features/{feature}/types.ts
export interface {Feature} {
  id: string;
  // ... fields
  created_at: string;
  updated_at: string;
}

export interface Create{Feature}Dto {
  // ... fields for creation
}
```

## 5. Create Skeleton Component

```tsx
// apps/web/src/features/{feature}/components/{feature}-skeleton.tsx
export function {Feature}Skeleton() {
  return (
    <div className="p-4 md:p-6 lg:p-8 space-y-6 animate-pulse">
      <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-48" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-48 bg-gray-200 dark:bg-gray-700 rounded-xl" />
        ))}
      </div>
    </div>
  );
}
```

## Checklist

- [ ] Page uses Server Component by default
- [ ] `metadata` defined for SEO
- [ ] `loading.tsx` created for Suspense fallback
- [ ] `error.tsx` created for error boundary
- [ ] Feature module created: components, hooks, api, types
- [ ] Skeleton component for loading states
- [ ] TanStack Query hooks for data fetching
- [ ] API functions using centralized `apiClient`
- [ ] Dark mode supported (`dark:` prefixed classes)
- [ ] Mobile responsive (mobile-first breakpoints)
- [ ] Vietnamese user-facing text
- [ ] Framer Motion animations where appropriate
