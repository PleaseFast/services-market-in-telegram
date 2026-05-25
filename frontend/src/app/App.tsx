import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { useEffect } from "react";
import { router } from "./router";
import { applyTelegramTheme, getInitData } from "@/lib/telegram";
import { useAuthStore } from "@/stores/auth";
import { http } from "@/lib/api";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
});

async function bootstrapTelegramAuth() {
  const initData = getInitData();
  if (!initData) return;
  const { accessToken, setTokens, setUser } = useAuthStore.getState();
  if (accessToken) return;
  try {
    const tokens = await http.post<{ access_token: string; refresh_token: string }>(
      "/auth/telegram",
      { init_data: initData, bot: "referee", role: "specialist" },
    );
    setTokens(tokens.access_token, tokens.refresh_token);
    const me = await http.get<{ id: string; email: string | null; role: "specialist" | "customer" }>(
      "/auth/me",
    );
    setUser(me);
  } catch {
    // user must pick role on landing
  }
}

export function App() {
  useEffect(() => {
    applyTelegramTheme();
    void bootstrapTelegramAuth();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}
