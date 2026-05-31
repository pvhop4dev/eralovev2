"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export interface EventPhoto {
  id: string;
  couple_id: string;
  uploaded_by: string;
  event_id: string | null;
  s3_key: string;
  thumbnail_key: string | null;
  original_url: string;
  thumbnail_url: string | null;
  caption: string | null;
  photo_date: string | null;
  location_name: string | null;
  latitude: number | null;
  longitude: number | null;
  width: number | null;
  height: number | null;
  file_size: number | null;
  mime_type: string | null;
  exif_data: Record<string, unknown> | null;
  created_at: string | null;
}

export interface AddPhotoInput {
  s3_key: string;
  original_url: string;
  thumbnail_key?: string;
  thumbnail_url?: string;
  caption?: string;
  photo_date?: string;
  location_name?: string;
  latitude?: number;
  longitude?: number;
  width?: number;
  height?: number;
  file_size?: number;
  mime_type?: string;
  exif_data?: Record<string, unknown>;
  event_id?: string;
}

export function useEventPhotos(eventId: string) {
  return useQuery<EventPhoto[]>({
    queryKey: ["photos", "event", eventId],
    queryFn: async () => {
      if (!eventId) return [];
      const response = await apiClient.get<{ photos: EventPhoto[] }>(
        `/api/v1/photos/event/${eventId}`,
      );
      return response?.photos || [];
    },
    enabled: !!eventId,
  });
}

export function useAddPhoto() {
  const queryClient = useQueryClient();
  return useMutation<EventPhoto, Error, AddPhotoInput>({
    mutationFn: async (input) => {
      return apiClient.post<EventPhoto>("/api/v1/photos", input);
    },
    onSuccess: (data) => {
      if (data.event_id) {
        queryClient.invalidateQueries({
          queryKey: ["photos", "event", data.event_id],
        });
      }
      queryClient.invalidateQueries({ queryKey: ["photos"] });
    },
  });
}

export function useDeletePhoto() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, { id: string; eventId?: string }>({
    mutationFn: async ({ id }) => {
      return apiClient.delete(`/api/v1/photos/${id}`);
    },
    onSuccess: (_, variables) => {
      if (variables.eventId) {
        queryClient.invalidateQueries({
          queryKey: ["photos", "event", variables.eventId],
        });
      }
      queryClient.invalidateQueries({ queryKey: ["photos"] });
    },
  });
}
