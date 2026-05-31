import { create } from "zustand";
import { persist } from "zustand/middleware";

import {
  DEFAULT_LANGUAGE,
  type Language,
  normalizeLanguage,
} from "@/i18n";

export type Role = "specialist" | "customer";

export interface AuthUser {
  id: string;
  email: string | null;
  role: Role;
  language?: Language;
  profile_complete?: boolean;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  isGuest: boolean;
  language: Language;
  setTokens: (a: string, r: string) => void;
  setUser: (u: AuthUser | null) => void;
  setProfileComplete: (value: boolean) => void;
  enterGuest: () => void;
  exitGuest: () => void;
  setLanguage: (lang: Language) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isGuest: false,
      language: DEFAULT_LANGUAGE,
      setTokens: (a, r) => set({ accessToken: a, refreshToken: r, isGuest: false }),
      setUser: (u) =>
        set((s) => ({
          user: u,
          isGuest: u ? false : false,
          language: u?.language ? normalizeLanguage(u.language) : s.language,
        })),
      setProfileComplete: (value) =>
        set((s) => (s.user ? { user: { ...s.user, profile_complete: value } } : {})),
      enterGuest: () =>
        set({ accessToken: null, refreshToken: null, user: null, isGuest: true }),
      exitGuest: () => set({ isGuest: false }),
      setLanguage: (lang) => set({ language: normalizeLanguage(lang) }),
      logout: () =>
        set({ accessToken: null, refreshToken: null, user: null, isGuest: false }),
    }),
    { name: "doings-auth" },
  ),
);
