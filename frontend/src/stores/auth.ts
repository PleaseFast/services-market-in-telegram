import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Role = "specialist" | "customer";

export interface AuthUser {
  id: string;
  email: string | null;
  role: Role;
  profile_complete?: boolean;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  isGuest: boolean;
  setTokens: (a: string, r: string) => void;
  setUser: (u: AuthUser | null) => void;
  setProfileComplete: (value: boolean) => void;
  enterGuest: () => void;
  exitGuest: () => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isGuest: false,
      setTokens: (a, r) => set({ accessToken: a, refreshToken: r, isGuest: false }),
      setUser: (u) => set({ user: u, isGuest: u ? false : false }),
      setProfileComplete: (value) =>
        set((s) => (s.user ? { user: { ...s.user, profile_complete: value } } : {})),
      enterGuest: () =>
        set({ accessToken: null, refreshToken: null, user: null, isGuest: true }),
      exitGuest: () => set({ isGuest: false }),
      logout: () =>
        set({ accessToken: null, refreshToken: null, user: null, isGuest: false }),
    }),
    { name: "doings-auth" },
  ),
);
