import { http } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

interface TokenPair {
  access_token: string;
  refresh_token: string;
}

interface UserOut {
  id: string;
  email: string | null;
  role: "specialist" | "customer";
  profile_complete?: boolean;
}

export async function register(email: string, password: string, role: "specialist" | "customer") {
  const tokens = await http.post<TokenPair>("/auth/register", { email, password, role });
  useAuthStore.getState().setTokens(tokens.access_token, tokens.refresh_token);
  const me = await http.get<UserOut>("/auth/me");
  useAuthStore.getState().setUser(me);
  return me;
}

export async function login(email: string, password: string) {
  const tokens = await http.post<TokenPair>("/auth/login", { email, password });
  useAuthStore.getState().setTokens(tokens.access_token, tokens.refresh_token);
  const me = await http.get<UserOut>("/auth/me");
  useAuthStore.getState().setUser(me);
  return me;
}
