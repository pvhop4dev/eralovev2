/**
 * Eralove — Shared Constants
 */

/** API version prefix */
export const API_PREFIX = "/api/v1";

/** Default pagination */
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

/** Upload limits */
export const MAX_PHOTO_SIZE_MB = 10;
export const MAX_PHOTOS_PER_EVENT = 20;
export const MAX_AVATAR_SIZE_MB = 5;

/** Message limits */
export const MAX_MESSAGE_LENGTH = 2000;
export const MAX_BIO_LENGTH = 500;
export const MAX_DISPLAY_NAME_LENGTH = 100;
export const MAX_USERNAME_LENGTH = 50;

/** Time constants (milliseconds) */
export const MATCH_REQUEST_EXPIRY_DAYS = 7;
export const SOFT_DELETE_RECOVERY_DAYS = 30;

/** Event types */
export const EVENT_TYPES = [
  "date",
  "anniversary",
  "travel",
  "birthday",
  "custom",
] as const;

export type EventType = (typeof EVENT_TYPES)[number];

/** Love languages */
export const LOVE_LANGUAGES = [
  "Words of Affirmation",
  "Acts of Service",
  "Receiving Gifts",
  "Quality Time",
  "Physical Touch",
] as const;

export type LoveLanguage = (typeof LOVE_LANGUAGES)[number];

/** Message types */
export const MESSAGE_TYPES = [
  "text",
  "image",
  "video",
  "voice",
  "file",
  "love_message",
  "secret",
  "draw",
] as const;

export type MessageType = (typeof MESSAGE_TYPES)[number];
