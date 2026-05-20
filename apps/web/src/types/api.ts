/**
 * Shared API Types for Eralove.
 *
 * These types mirror the backend ApiResponse format.
 */

/** Unified API response wrapper. */
export interface ApiResponse<T> {
  data: T | null;
  meta: PaginationMeta | null;
  error: ApiError | null;
}

/** Pagination metadata. */
export interface PaginationMeta {
  page?: number;
  per_page?: number;
  total?: number;
  cursor?: string;
  has_next: boolean;
}

/** API error detail. */
export interface ApiError {
  code: string;
  message: string;
  field?: string;
  details?: Array<{ field?: string; message: string }>;
}

/** Base entity with timestamps. */
export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string | null;
}
