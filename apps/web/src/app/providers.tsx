"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { Toaster } from "sonner";
import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";

const WALLPAPERS = {
  primary: "linear-gradient(135deg, #FFF0F5 0%, #F3E8FF 50%, #FFF0F5 100%)",
  warm: "linear-gradient(135deg, #FFF7ED 0%, #FFE4E6 50%, #FFF7ED 100%)",
  cool: "linear-gradient(135deg, #ECFDF5 0%, #EEF2F6 50%, #ECFDF5 100%)",
  deep: "linear-gradient(135deg, #FAF5FF 0%, #F5F3FF 50%, #FAF5FF 100%)",
};

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            retry: 2,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  useEffect(() => {
    // Register token provider for the API client
    apiClient.setTokenProvider(() => useAuthStore.getState().accessToken);

    const saved = localStorage.getItem("eralove_wallpaper");
    if (saved && saved in WALLPAPERS) {
      document.documentElement.style.setProperty(
        "--gradient-bg",
        WALLPAPERS[saved as keyof typeof WALLPAPERS],
      );
    }
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        {children}
        <Toaster
          position="top-right"
          richColors
          toastOptions={{
            style: {
              borderRadius: "12px",
              fontFamily: "var(--font-body)",
            },
          }}
        />
      </ThemeProvider>
    </QueryClientProvider>
  );
}
