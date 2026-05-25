import { useAuthStore } from "@/stores/auth";

const BASE_URL = (import.meta as any).env.VITE_API_BASE_URL ?? "/api/v1";

export class ApiError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
  }
}

async function refreshAccess(): Promise<string | null> {
  const { refreshToken, setTokens, logout } = useAuthStore.getState();
  if (!refreshToken) return null;
  const res = await fetch(`${BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!res.ok) {
    logout();
    return null;
  }
  const data = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return data.access_token as string;
}

export async function api<T = unknown>(
  path: string,
  init: RequestInit & { skipAuth?: boolean } = {},
): Promise<T> {
  const { accessToken } = useAuthStore.getState();
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (accessToken && !init.skipAuth) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  let res = await fetch(`${BASE_URL}${path}`, { ...init, headers });

  if (res.status === 401 && !init.skipAuth) {
    const fresh = await refreshAccess();
    if (fresh) {
      headers.set("Authorization", `Bearer ${fresh}`);
      res = await fetch(`${BASE_URL}${path}`, { ...init, headers });
    }
  }

  const text = await res.text();
  const json = text ? JSON.parse(text) : null;
  if (!res.ok) {
    throw new ApiError(res.status, json?.detail ?? res.statusText);
  }
  return json as T;
}

export const http = {
  get: <T>(p: string) => api<T>(p),
  post: <T>(p: string, body?: unknown) => api<T>(p, { method: "POST", body: JSON.stringify(body ?? {}) }),
  put: <T>(p: string, body?: unknown) => api<T>(p, { method: "PUT", body: JSON.stringify(body ?? {}) }),
  patch: <T>(p: string, body?: unknown) => api<T>(p, { method: "PATCH", body: JSON.stringify(body ?? {}) }),
  del: <T>(p: string) => api<T>(p, { method: "DELETE" }),
};
