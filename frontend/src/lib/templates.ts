import type { ProjectTemplate } from "@/features/projects/types";

export const CATEGORY_ORDER = [
  "Frontend",
  "Backend",
  "Mobile",
  "Bots",
  "AI",
  "Data",
  "DevOps",
  "Design",
] as const;

export type TemplateGroup = { category: string; items: ProjectTemplate[] };

export function groupByCategory(templates: ProjectTemplate[]): TemplateGroup[] {
  const map = new Map<string, ProjectTemplate[]>();
  for (const t of templates) {
    const arr = map.get(t.category) ?? [];
    arr.push(t);
    map.set(t.category, arr);
  }
  const rank = new Map<string, number>(
    CATEGORY_ORDER.map((c, i) => [c, i]),
  );
  return Array.from(map.entries())
    .map(([category, items]) => ({ category, items }))
    .sort((a, b) => {
      const ra = rank.get(a.category) ?? 999;
      const rb = rank.get(b.category) ?? 999;
      if (ra !== rb) return ra - rb;
      return a.category.localeCompare(b.category);
    });
}
