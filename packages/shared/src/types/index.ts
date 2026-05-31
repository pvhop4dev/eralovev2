/**
 * Eralove — Shared Types
 */

/** Basic user info (public-facing). */
export interface UserPublic {
  id: string;
  display_name: string;
  username: string;
  avatar_url: string | null;
  zodiac_sign: string | null;
}

/** Couple status. */
export type CoupleStatus = "active" | "paused" | "broken_up";

/** Match request status. */
export type MatchRequestStatus =
  | "pending"
  | "accepted"
  | "declined"
  | "expired";

/** Message status. */
export type MessageStatus = "sent" | "delivered" | "read";

/** Mood emoji set. */
export const MOOD_EMOJIS = [
  "😊",
  "😍",
  "🥰",
  "😢",
  "😤",
  "😴",
  "🤗",
  "😎",
  "🥺",
  "😈",
] as const;

export type MoodEmoji = (typeof MOOD_EMOJIS)[number];
