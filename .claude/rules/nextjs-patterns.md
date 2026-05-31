---
name: nextjs-patterns
description: Next.js 15 App Router patterns — routing, layouts, middleware, SSR, server actions, and optimization
---

# Next.js 15 App Router Rules

## Routing Structure

```
apps/web/src/app/
├── (auth)/                    # Auth route group (no layout nesting)
│   ├── login/page.tsx
│   ├── register/page.tsx
│   └── onboarding/page.tsx
├── (main)/                    # Main app route group (shared layout with sidebar/nav)
│   ├── layout.tsx             # Main layout: sidebar + header + WebSocket init
│   ├── page.tsx               # Dashboard (Home)
│   ├── calendar/
│   │   ├── page.tsx           # Calendar view
│   │   └── [eventId]/page.tsx # Event detail
│   ├── chat/page.tsx          # Chat view
│   ├── map/page.tsx           # Love Map
│   ├── ari/page.tsx           # Mascot Ari
│   ├── quests/page.tsx        # Love Quests & Quiz
│   ├── shared/                # Shared Space
│   │   ├── notes/page.tsx
│   │   ├── todos/page.tsx
│   │   └── fund/page.tsx
│   ├── store/page.tsx         # Gift Store
│   ├── settings/
│   │   ├── page.tsx           # Settings main
│   │   └── profile/page.tsx   # Profile edit
│   └── photos/page.tsx        # Photo gallery
├── layout.tsx                 # Root layout (providers, fonts, metadata)
├── not-found.tsx              # 404 page
├── error.tsx                  # Error boundary
├── loading.tsx                # Global loading
└── globals.css
```

## Route Groups

### `(auth)` — Unauthenticated Pages

```tsx
// app/(auth)/layout.tsx
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 to-purple-50 dark:from-gray-950 dark:to-purple-950">
      {children}
    </div>
  );
}
```

### `(main)` — Authenticated Pages

```tsx
// app/(main)/layout.tsx
import { redirect } from "next/navigation";
import { getServerSession } from "@/lib/auth-server";

export default async function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession();
  if (!session) redirect("/login");

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Header user={session.user} />
        {children}
      </main>
      <SocketProvider />
    </div>
  );
}
```

## Page Patterns

### Server Component Page (Default)

```tsx
// app/(main)/calendar/page.tsx
import { Suspense } from "react";
import { CalendarView } from "@/features/calendar/components/calendar-view";
import { CalendarSkeleton } from "@/features/calendar/components/calendar-skeleton";

export const metadata = {
  title: "Lịch Tình Yêu | Eralove",
  description: "Quản lý sự kiện và kỷ niệm của hai bạn",
};

export default function CalendarPage() {
  return (
    <div className="p-4 md:p-6 lg:p-8">
      <h1 className="text-2xl font-heading font-bold text-purple-900 dark:text-pink-100">
        📅 Lịch Tình Yêu
      </h1>
      <Suspense fallback={<CalendarSkeleton />}>
        <CalendarView />
      </Suspense>
    </div>
  );
}
```

### Client Component Page (Interactive)

```tsx
// app/(main)/chat/page.tsx
"use client";

import { ChatView } from "@/features/chat/components/chat-view";

export default function ChatPage() {
  return <ChatView />;
}
```

### Dynamic Route Page

```tsx
// app/(main)/calendar/[eventId]/page.tsx
import { notFound } from "next/navigation";
import { fetchEvent } from "@/features/calendar/api";

interface Props {
  params: Promise<{ eventId: string }>;
}

export async function generateMetadata({ params }: Props) {
  const { eventId } = await params;
  const event = await fetchEvent(eventId);
  return {
    title: event ? `${event.title} | Eralove` : "Sự kiện không tồn tại",
  };
}

export default async function EventDetailPage({ params }: Props) {
  const { eventId } = await params;
  const event = await fetchEvent(eventId);
  if (!event) notFound();

  return <EventDetail event={event} />;
}
```

## Middleware (Route Protection)

```typescript
// apps/web/src/middleware.ts
import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login", "/register", "/onboarding", "/forgot-password"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("refresh_token")?.value;

  // Public paths — allow without auth
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    if (token) {
      // Already logged in, redirect to dashboard
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  // Protected paths — require auth
  if (!token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    // Match all paths except static files and API
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
```

## Root Layout (Providers)

```tsx
// app/layout.tsx
import { Nunito, Inter } from "next/font/google";
import { Providers } from "./providers";
import "./globals.css";

const nunito = Nunito({
  subsets: ["latin", "vietnamese"],
  variable: "--font-heading",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata = {
  title: {
    template: "%s | Eralove",
    default: "Eralove — Nơi lưu giữ mọi khoảnh khắc yêu thương",
  },
  description:
    "Ứng dụng dành riêng cho các cặp đôi — lưu giữ ký ức, kết nối mỗi ngày.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body
        className={`${nunito.variable} ${inter.variable} font-sans antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

### Providers Wrapper

```tsx
// app/providers.tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { Toaster } from "sonner";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        {children}
        <Toaster position="top-right" richColors />
      </ThemeProvider>
    </QueryClientProvider>
  );
}
```

## Loading & Error States

### Loading UI (Skeleton)

```tsx
// app/(main)/calendar/loading.tsx
import { CalendarSkeleton } from "@/features/calendar/components/calendar-skeleton";

export default function CalendarLoading() {
  return <CalendarSkeleton />;
}
```

### Error Boundary

```tsx
// app/(main)/calendar/error.tsx
"use client";

export default function CalendarError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <h2 className="text-xl font-heading text-rose-500">Đã xảy ra lỗi</h2>
      <p className="text-gray-500 mt-2">{error.message}</p>
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 bg-rose-500 text-white rounded-full"
      >
        Thử lại
      </button>
    </div>
  );
}
```

## Image Optimization

```tsx
// ALWAYS use next/image
import Image from "next/image";

// For S3/CDN images
<Image
  src={photo.url}
  alt={photo.caption || "Ảnh kỷ niệm"}
  width={600}
  height={400}
  className="rounded-xl object-cover"
  placeholder="blur"
  blurDataURL={photo.blur_hash}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
/>;

// next.config.ts — allow S3 domain
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cdn-love.eraquix.com",
      },
      {
        protocol: "https",
        hostname: "eralove-media.s3.ap-southeast-1.amazonaws.com",
      },
    ],
  },
};
```

## Dynamic Imports (Code Splitting)

```tsx
import dynamic from "next/dynamic";

// Heavy components — lazy load
const MapView = dynamic(
  () => import("@/features/map/components/map-view").then((m) => m.MapView),
  {
    loading: () => <MapSkeleton />,
    ssr: false, // Mapbox doesn't support SSR
  },
);

const ChatView = dynamic(
  () => import("@/features/chat/components/chat-view").then((m) => m.ChatView),
  {
    loading: () => <ChatSkeleton />,
    ssr: false, // WebSocket client-only
  },
);

const EmojiPicker = dynamic(
  () => import("@/components/molecules/emoji-picker"),
  { ssr: false },
);
```

## Metadata & SEO

```tsx
// Per-page metadata
export const metadata = {
  title: "Lịch Tình Yêu", // Template from root: "Lịch Tình Yêu | Eralove"
  description: "Quản lý sự kiện, kỷ niệm và những ngày đặc biệt của hai bạn.",
  openGraph: {
    title: "Eralove — Lịch Tình Yêu",
    description: "Nơi lưu giữ mọi khoảnh khắc yêu thương",
    images: ["/og-image.png"],
  },
};
```

## Rules

### MUST

- Use App Router (not Pages Router)
- Server Components by default, `"use client"` only when needed
- Use `next/image` for all images (never `<img>`)
- Use `next/font` for fonts (never CDN link in `<head>`)
- Use `next/link` for navigation (never `<a>` for internal links)
- Define `metadata` or `generateMetadata` on every page
- Use route groups `(auth)` and `(main)` for layout separation
- Use `loading.tsx` for Suspense fallback on every route
- Use `error.tsx` for error boundaries on feature routes

### MUST NOT

- Never use `useEffect` for data fetching in Server Components
- Never expose server-only code (DB queries, secrets) in Client Components
- Never use `window`, `document`, `localStorage` in Server Components
- Never import heavy client libraries (Mapbox, Socket.IO) without dynamic import + `ssr: false`
- Never use `router.push()` for programmatic navigation in Server Components (use `redirect()`)

### SHOULD

- Use `Suspense` boundaries for parallel data loading
- Use `generateStaticParams` for known dynamic routes
- Implement proper `not-found.tsx` for user-friendly 404
- Vietnamese language for all user-facing text in the app
- Use `next-themes` for dark mode with `attribute="class"`
