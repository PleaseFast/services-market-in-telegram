import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { http } from "@/lib/api";
import type {
  Page,
  Review,
  ServiceCatalogItem,
  SpecialistProfile,
  SpecialistService,
  TimelineItem,
  TimelineKind,
} from "../projects/types";

// ---------- Profile ----------

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
  categories: string[];
  years_experience: number;
  bio: string;
  avatar_id: string;
}

export function useSaveProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ProfileInput) => http.put<SpecialistProfile>("/specialists/me", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["specialist", "me"] }),
  });
}

// ---------- Timeline (per-item CRUD) ----------

export interface TimelineItemInput {
  kind: TimelineKind;
  title: string;
  description: string;
  start_year: number;
  end_year: number | null;
  is_current: boolean;
}

export type TimelineItemPatch = Partial<TimelineItemInput>;

export function useMyTimeline(kind?: TimelineKind) {
  const qs = kind ? `?kind=${kind}` : "";
  return useQuery({
    queryKey: ["specialist", "me", "timeline", kind ?? "all"],
    queryFn: () => http.get<TimelineItem[]>(`/specialists/me/timeline${qs}`),
  });
}

function invalidateTimeline(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ["specialist", "me", "timeline"] });
  qc.invalidateQueries({ queryKey: ["specialist", "me"] });
}

export function useCreateTimelineItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: TimelineItemInput) =>
      http.post<TimelineItem>("/specialists/me/timeline", input),
    onSuccess: () => invalidateTimeline(qc),
  });
}

export function usePatchTimelineItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, patch }: { id: string; patch: TimelineItemPatch }) =>
      http.patch<TimelineItem>(`/specialists/me/timeline/${id}`, patch),
    onSuccess: () => invalidateTimeline(qc),
  });
}

export function useDeleteTimelineItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => http.del<void>(`/specialists/me/timeline/${id}`),
    onSuccess: () => invalidateTimeline(qc),
  });
}

export function useMoveTimelineItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, direction }: { id: string; direction: "up" | "down" }) =>
      http.post<TimelineItem>(`/specialists/me/timeline/${id}/move`, { direction }),
    onSuccess: () => invalidateTimeline(qc),
  });
}

// ---------- Services catalog + bindings ----------

export function useServiceCatalog() {
  return useQuery({
    queryKey: ["services", "catalog"],
    queryFn: () => http.get<ServiceCatalogItem[]>("/services/catalog"),
    staleTime: 5 * 60 * 1000, // 5 min — rarely changes
  });
}

export interface ServiceInput {
  slug: string;
  price_amount: string | number;
  price_currency?: string;
}

export function useReplaceMyServices() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (items: ServiceInput[]) =>
      http.put<void>("/specialists/me/services", { items }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["specialist", "me"] });
    },
  });
}

// ---------- Reviews ----------

export function useUserReviews(userId: string | undefined) {
  return useQuery({
    queryKey: ["reviews", userId],
    enabled: !!userId,
    queryFn: () => http.get<Page<Review>>(`/users/${userId}/reviews?limit=50`),
  });
}

// ---------- Public specialist profile (read-only by user_id) ----------

export function usePublicSpecialist(userId: string | undefined) {
  return useQuery({
    queryKey: ["specialist", "public", userId],
    enabled: !!userId,
    queryFn: () => http.get<SpecialistProfile>(`/specialists/${userId}`),
  });
}

// ---------- Specialists directory ----------

export function useSpecialistsDirectory() {
  return useQuery({
    queryKey: ["specialists", "directory"],
    queryFn: () => http.get<Page<SpecialistProfile>>("/specialists?limit=50"),
  });
}
