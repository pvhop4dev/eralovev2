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

  private async request<T>(
    method: string,
    path: string,
    options?: {
      body?: unknown;
      params?: Record<string, string>;
      headers?: Record<string, string>;
    }
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
      const error = new Error(json.error?.message || "An error occurred") as Error & {
        code: string;
        status: number;
        details?: Record<string, unknown>[];
      };
      error.code = json.error?.code || "UNKNOWN_ERROR";
      error.status = response.status;
      error.details = json.error?.details;

      // TODO: Handle 401 — refresh token and retry

      throw error;
    }

    return json.data as T;
  }

  async get<T>(path: string, options?: { params?: Record<string, string> }): Promise<T> {
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
