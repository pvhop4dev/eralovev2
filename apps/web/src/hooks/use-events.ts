"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export interface LoveEvent {
  id: string;
  couple_id: string;
  created_by: string;
  title: string;
  description: string | null;
  event_type: string;
  event_date: string;
  event_time: string | null;
  end_date: string | null;
  location_name: string | null;
  latitude: number | null;
  longitude: number | null;
  icon: string;
  color: string | null;
  is_recurring: boolean;
  recurrence_rule: string | null;
  reminder_before: string | null;
}

export interface CreateEventInput {
  title: string;
  event_type: string;
  event_date: string;
  event_time?: string;
  description?: string;
  location_name?: string;
  latitude?: number;
  longitude?: number;
  is_recurring?: boolean;
  recurrence_rule?: string;
  reminder_before?: string;
}

export interface UpdateEventInput {
  id: string;
  title?: string;
  event_type?: string;
  event_date?: string;
  event_time?: string;
  description?: string;
  location_name?: string;
  latitude?: number;
  longitude?: number;
  is_recurring?: boolean;
  recurrence_rule?: string;
  reminder_before?: string;
}

export function useEvents(year: number, month: number) {
  return useQuery<LoveEvent[]>({
    queryKey: ["events", year, month],
    queryFn: async () => {
      const response = await apiClient.get<{ events: LoveEvent[] }>(
        "/api/v1/events",
        {
          params: {
            year: String(year),
            month: String(month),
          },
        },
      );
      return response?.events || [];
    },
  });
}

export function useCreateEvent() {
  const queryClient = useQueryClient();
  return useMutation<LoveEvent, Error, CreateEventInput>({
    mutationFn: async (input) => {
      return apiClient.post<LoveEvent>("/api/v1/events", input);
    },
    onSuccess: (data) => {
      // Invalidate events list for that event date's year & month
      const eventDate = new Date(data.event_date);
      queryClient.invalidateQueries({
        queryKey: ["events", eventDate.getFullYear(), eventDate.getMonth() + 1],
      });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateEvent() {
  const queryClient = useQueryClient();
  return useMutation<LoveEvent, Error, UpdateEventInput>({
    mutationFn: async ({ id, ...body }) => {
      return apiClient.patch<LoveEvent>(`/api/v1/events/${id}`, body);
    },
    onSuccess: (data) => {
      // Invalidate events list
      const eventDate = new Date(data.event_date);
      queryClient.invalidateQueries({
        queryKey: ["events", eventDate.getFullYear(), eventDate.getMonth() + 1],
      });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDeleteEvent() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, { id: string; eventDate: string }>({
    mutationFn: async ({ id }) => {
      return apiClient.delete(`/api/v1/events/${id}`);
    },
    onSuccess: (_, variables) => {
      const eventDate = new Date(variables.eventDate);
      queryClient.invalidateQueries({
        queryKey: ["events", eventDate.getFullYear(), eventDate.getMonth() + 1],
      });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export interface CalendarHeaderData {
  solar_date: {
    iso: string;
    day_name: string;
    formatted: string;
  };
  lunar_date: string;
  weather: {
    temp: number;
    condition: string;
    emoji: string;
    windspeed: number;
  };
  daily_quote: {
    text: string;
    author: string;
  };
  days_together: number;
  horoscope: {
    user: {
      sign: string;
      prediction: string;
    };
    partner: {
      name: string;
      sign: string;
      prediction: string;
    } | null;
  };
  feng_shui: {
    direction: string;
    lucky_color: string;
    good_for: string;
    avoid: string;
  };
}

export function useCalendarHeader(
  latitude?: number | null,
  longitude?: number | null,
) {
  return useQuery<CalendarHeaderData>({
    queryKey: ["calendarHeader", latitude, longitude],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (latitude !== undefined && latitude !== null) {
        params.latitude = String(latitude);
      }
      if (longitude !== undefined && longitude !== null) {
        params.longitude = String(longitude);
      }
      return apiClient.get<CalendarHeaderData>("/api/v1/events/header", {
        params,
      });
    },
  });
}
