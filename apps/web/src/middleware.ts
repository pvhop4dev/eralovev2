import { NextResponse, type NextRequest } from "next/server";

/**
 * Next.js Middleware — Route Protection
 *
 * - Public routes: /, /login, /register, /forgot-password, /verify-email
 * - Protected routes: /dashboard, /chat, /calendar, /settings, etc.
 *
 * Auth check is done via the presence of the refresh token cookie.
 * Full token validation happens server-side on API calls.
 */

const PUBLIC_ROUTES = new Set([
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/verify-email",
  "/reset-password",
]);

const AUTH_ROUTES = new Set([
  "/login",
  "/register",
  "/forgot-password",
]);

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for refresh token cookie (basic auth indicator)
  const hasAuth = request.cookies.has("eralove_refresh_token");

  // Skip API routes, static files, etc.
  if (
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // Redirect authenticated users away from auth pages
  if (hasAuth && AUTH_ROUTES.has(pathname)) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Redirect unauthenticated users to login for protected routes
  if (!hasAuth && !PUBLIC_ROUTES.has(pathname)) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
