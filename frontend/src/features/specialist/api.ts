import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { http } from "@/lib/api";
import type { SpecialistProfile } from "../projects/types";

export function useMyProfile() {
  return useQuery({
    queryKey: ["specialist", "me"],
    queryFn: async () => {
      try {
        return await http.get<SpecialistProfile>("/specialists/me");
      } catch (e: unknown) {
        if ((e as { status?: number }).status === 404) return null;
        throw e;
      }
    },
  });
}

export interface ProfileInput {
  full_name: string;
  age: number;
  category: string;
  years_experience: number;
  bio: string;
  avatar_url?: string | null;
  workplaces: { title: string; company: string; period?: string | null }[];
  portfolio_links: { url: string; label?: string | null }[];
}

export function useSaveProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ProfileInput) => http.put<SpecialistProfile>("/specialists/me", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["specialist", "me"] }),
  });
}
