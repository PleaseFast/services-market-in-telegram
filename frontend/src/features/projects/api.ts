import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { http } from "@/lib/api";
import type { Application, Page, Project, ProjectTemplate } from "./types";

export function useTemplates() {
  return useQuery({
    queryKey: ["templates"],
    queryFn: () => http.get<ProjectTemplate[]>("/projects/templates"),
  });
}

export function usePublicFeed(category?: string) {
  return useQuery({
    queryKey: ["projects", "feed", category],
    queryFn: () =>
      http.get<Page<Project>>(
        `/projects?limit=50${category ? `&category=${encodeURIComponent(category)}` : ""}`,
      ),
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
