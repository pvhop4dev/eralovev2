"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { LoveEvent } from "./use-events";

export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  username: string;
  avatar_url: string | null;
  date_of_birth: string | null;
  gender: string | null;
  zodiac_sign: string | null;
  love_language: string | null;
  bio: string | null;
}

export interface CoupleProfile {
  id: string;
  user1_id: string;
  user2_id: string;
  start_date: string;
  couple_photo_url: string | null;
  status: string;
  theme_color: string;
  wallpaper_url: string | null;
}

export interface DailyQuote {
  text: string;
  author: string;
}

export interface DashboardData {
  user: UserProfile;
  couple: CoupleProfile | null;
  partner: UserProfile | null;
  days_together: number;
  daily_quote: DailyQuote;
  upcoming_events: (LoveEvent & { days_until: number })[];
  memory_flashback: LoveEvent[];
}

export interface MoodCheckinInput {
  mood_emoji: string;
  mood_note?: string;
}

export function useDashboardData() {
  return useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: async () => {
      return apiClient.get<DashboardData>("/api/v1/dashboard");
    },
  });
}

export function useCheckinMood() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, MoodCheckinInput>({
    mutationFn: async (input) => {
      return apiClient.post<void>("/api/v1/mood/checkin", input);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
