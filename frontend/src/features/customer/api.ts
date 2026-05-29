import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { http } from "@/lib/api";
import type { CustomerPublic, Project } from "../projects/types";

export interface CustomerProfileInput {
  display_name: string;
  avatar_id: string;
}

export function useMyCustomerProfile() {
  return useQuery({
    queryKey: ["customer", "me"],
    queryFn: async () => {
      try {
        return await http.get<CustomerPublic>("/customers/me");
      } catch (e: unknown) {
        if ((e as { status?: number }).status === 404) return null;
        throw e;
      }
    },
  });
}

export function useSaveCustomerProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CustomerProfileInput) =>
      http.put<CustomerPublic>("/customers/me", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["customer", "me"] }),
  });
}

export function usePublicCustomer(userId: string | undefined) {
  return useQuery({
    queryKey: ["customer", "public", userId],
    enabled: !!userId,
    queryFn: () => http.get<CustomerPublic>(`/customers/${userId}`),
  });
}

export function useCustomerOpenProjects(userId: string | undefined) {
  return useQuery({
    queryKey: ["customer", "open-projects", userId],
    enabled: !!userId,
    queryFn: () => http.get<Project[]>(`/customers/${userId}/open-projects?limit=20`),
  });
}
