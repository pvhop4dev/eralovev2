/**
 * Centralized API Client for Eralove.
 *
 * All API calls MUST go through this client.
 * Handles: auth token injection, refresh on 401, error formatting.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiError {
  code: string;
  message: string;
  field?: string;
  details?: Record<string, unknown>[];
}

interface ApiResponse<T> {
  data: T | null;
  meta: {
    page?: number;
    per_page?: number;
    total?: number;
    cursor?: string;
    has_next?: boolean;
  } | null;
  error: ApiError | null;
}

class ApiClient {
  private baseUrl: string;
  private getToken: (() => string | null) | null = null;
  private isRefreshing = false;
  private refreshSubscribers: ((token: string) => void)[] = [];

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Set the token provider function.
   * Called lazily to avoid circular imports with auth store.
   */
  setTokenProvider(fn: () => string | null) {
    this.getToken = fn;
  }

  private onTokenRefreshed(token: string) {
    this.refreshSubscribers.forEach((cb) => cb(token));
    this.refreshSubscribers = [];
  }

  private addRefreshSubscriber(cb: (token: string) => void) {
    this.refreshSubscribers.push(cb);
  }

  private async handleTokenRefresh(): Promise<string> {
    if (this.isRefreshing) {
      return new Promise<string>((resolve) => {
        this.addRefreshSubscriber((token) => {
          resolve(token);
        });
      });
    }

    this.isRefreshing = true;

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // send refresh cookie
      });

      if (!response.ok) {
        throw new Error("Failed to refresh token");
      }

      const json = await response.json();
      const newToken = json.data?.access_token;
      if (!newToken) {
        throw new Error("Access token not returned from refresh endpoint");
      }

      // Update Zustand auth store
      // Dynamic import to avoid circular dependencies
      const { useAuthStore } = await import("../stores/auth-store");
      useAuthStore.getState().setToken(newToken);

      this.onTokenRefreshed(newToken);
      return newToken;
    } catch (error) {
      // Clear token and logout
      const { useAuthStore } = await import("../stores/auth-store");
      useAuthStore.getState().logout();

      // Redirect to login if on client-side
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }

      this.refreshSubscribers = []; // Clear queue on failure
      throw error;
    } finally {
      this.isRefreshing = false;
    }
  }

  private async request<T>(
    method: string,
    path: string,
    options?: {
      body?: unknown;
      params?: Record<string, string>;
      headers?: Record<string, string>;
    },
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);

    if (options?.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        url.searchParams.set(key, value);
      });
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...options?.headers,
    };

    // Inject auth token
    const token = this.getToken?.();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url.toString(), {
      method,
      headers,
      body: options?.body ? JSON.stringify(options.body) : undefined,
      credentials: "include", // Include cookies (refresh token)
    });

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    const json: ApiResponse<T> = await response.json();

    // Handle errors
    if (!response.ok || json.error) {
      const error = new Error(
        json.error?.message || "An error occurred",
      ) as Error & {
        code: string;
        status: number;
        details?: Record<string, unknown>[];
      };
      error.code = json.error?.code || "UNKNOWN_ERROR";
      error.status = response.status;
      error.details = json.error?.details;

      // Handle 401 — refresh token and retry
      if (
        response.status === 401 &&
        !path.includes("/auth/login") &&
        !path.includes("/auth/register") &&
        !path.includes("/auth/refresh")
      ) {
        try {
          const newToken = await this.handleTokenRefresh();
          // Retry original request with new token
          const updatedOptions = {
            ...options,
            headers: {
              ...options?.headers,
              Authorization: `Bearer ${newToken}`,
            },
          };
          return this.request<T>(method, path, updatedOptions);
        } catch {
          throw error; // throw original 401 error if refresh failed
        }
      }

      throw error;
    }

    return json.data as T;
  }

  async get<T>(
    path: string,
    options?: { params?: Record<string, string> },
  ): Promise<T> {
    return this.request<T>("GET", path, options);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("POST", path, { body });
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("PATCH", path, { body });
  }

  async delete(path: string): Promise<void> {
    return this.request<void>("DELETE", path);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
