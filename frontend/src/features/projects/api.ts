import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { http } from "@/lib/api";
import type { Application, Page, Project, ProjectTemplate } from "./types";

export function useTemplates() {
  return useQuery({
    queryKey: ["templates"],
    queryFn: () => http.get<ProjectTemplate[]>("/projects/templates"),
  });
}

export type FeedSort = "newest" | "viewed";

export interface FeedFilters {
  q?: string;
  budget_min?: number;
  budget_max?: number;
  sort?: FeedSort;
}

function buildFeedQuery(filters: FeedFilters): string {
  const params = new URLSearchParams();
  params.set("limit", "50");
  if (filters.q && filters.q.trim()) params.set("q", filters.q.trim());
  if (filters.budget_min !== undefined && !Number.isNaN(filters.budget_min)) {
    params.set("budget_min", String(filters.budget_min));
  }
  if (filters.budget_max !== undefined && !Number.isNaN(filters.budget_max)) {
    params.set("budget_max", String(filters.budget_max));
  }
  if (filters.sort && filters.sort !== "newest") params.set("sort", filters.sort);
  return params.toString();
}

export function usePublicFeed(filters: FeedFilters = {}) {
  const qs = buildFeedQuery(filters);
  return useQuery({
    queryKey: ["projects", "feed", filters],
    queryFn: () => http.get<Page<Project>>(`/projects?${qs}`),
  });
}

export function useMyCustomerProjects() {
  return useQuery({
    queryKey: ["projects", "mine", "customer"],
    queryFn: () => http.get<Page<Project>>("/projects/mine/customer?limit=100"),
  });
}

export function useMySpecialistProjects() {
  return useQuery({
    queryKey: ["projects", "mine", "specialist"],
    queryFn: () => http.get<Page<Project>>("/projects/mine/specialist?limit=100"),
  });
}

export function useProject(id: string | undefined) {
  return useQuery({
    queryKey: ["project", id],
    enabled: !!id,
    queryFn: () => http.get<Project>(`/projects/${id}`),
  });
}

export function useApplicants(projectId: string | undefined) {
  return useQuery({
    queryKey: ["project", projectId, "applicants"],
    enabled: !!projectId,
    queryFn: () => http.get<Application[]>(`/projects/${projectId}/applications`),
  });
}

interface CreateProjectInput {
  title: string;
  description: string;
  budget: number;
  currency?: string;
  deadline?: string | null;
  template_id?: string | null;
  category?: string | null;
  publish?: boolean;
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateProjectInput) => http.post<Project>("/projects", input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function usePublishProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => http.post<Project>(`/projects/${id}/publish`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useApply() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, coverLetter }: { projectId: string; coverLetter?: string }) =>
      http.post<Application>(`/projects/${projectId}/applications`, {
        cover_letter: coverLetter ?? null,
      }),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["project", vars.projectId] });
    },
  });
}

export function useSelectSpecialist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, specialistId }: { projectId: string; specialistId: string }) =>
      http.post<Project>(`/projects/${projectId}/select-specialist/${specialistId}`),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["project", vars.projectId] });
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useCompleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => http.post<Project>(`/projects/${id}/complete`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useArchiveProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => http.post<Project>(`/projects/${id}/archive`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function usePauseProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => http.post<Project>(`/projects/${id}/pause`),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["project", id] });
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useResumeProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => http.post<Project>(`/projects/${id}/resume`),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["project", id] });
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => http.del<void>(`/projects/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export interface UpdateProjectInput {
  title?: string;
  description?: string;
  budget?: number;
  currency?: string;
  deadline?: string | null;
  category?: string | null;
}

export function useUpdateProject(id: string | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: UpdateProjectInput) =>
      http.patch<Project>(`/projects/${id}`, input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["project", id] });
      qc.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
