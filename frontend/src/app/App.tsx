import "@/i18n";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { useEffect } from "react";
import { router } from "./router";
import { applyTelegramTheme, getInitData } from "@/lib/telegram";
import { useAuthStore } from "@/stores/auth";
import { http } from "@/lib/api";
import i18n, { type Language, normalizeLanguage } from "@/i18n";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
});

async function syncLanguageWithServer() {
  const { accessToken, language, setLanguage } = useAuthStore.getState();
  if (!accessToken) return;
  try {
    const remote = await http.get<{ language: Language }>("/users/me/language");
    const normalized = normalizeLanguage(remote.language);
    if (normalized !== language) {
      setLanguage(normalized);
      await i18n.changeLanguage(normalized);
    } else if (normalized !== i18n.language) {
      await i18n.changeLanguage(normalized);
    }
  } catch {
    /* ignore — keep local language */
  }
}

async function bootstrapTelegramAuth() {
  const initData = getInitData();
  if (!initData) return;
  const { accessToken, isGuest, setTokens, setUser } = useAuthStore.getState();
  if (accessToken || isGuest) return;
  try {
    const tokens = await http.post<{ access_token: string; refresh_token: string }>(
      "/auth/telegram",
      { init_data: initData, bot: "referee", role: "specialist" },
    );
    setTokens(tokens.access_token, tokens.refresh_token);
    const me = await http.get<{
      id: string;
      email: string | null;
      role: "specialist" | "customer";
      language?: Language;
      profile_complete?: boolean;
    }>("/auth/me");
    setUser(me);
  } catch {
    // user must pick role on landing
  }
}

export function App() {
  useEffect(() => {
    applyTelegramTheme();
    void (async () => {
      await bootstrapTelegramAuth();
      await syncLanguageWithServer();
    })();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}
