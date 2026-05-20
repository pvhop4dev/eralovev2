/**
 * Auth Store — Zustand store for authentication state.
 *
 * Manages: user session, access token, login/logout.
 * Access token stored in memory only (never localStorage).
 */

import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  display_name: string;
  username: string;
  avatar_url: string | null;
  is_onboarded: boolean;
}

interface AuthState {
  // State
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;

  // Actions
  setAuth: (user: User, token: string) => void;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      setAuth: (user, token) =>
        set(
          { user, accessToken: token, isAuthenticated: true },
          undefined,
          "auth/setAuth"
        ),

      setToken: (token) =>
        set({ accessToken: token }, undefined, "auth/setToken"),

      logout: () =>
        set(
          { user: null, accessToken: null, isAuthenticated: false },
          undefined,
          "auth/logout"
        ),
    }),
    { name: "auth-store" }
  )
);
