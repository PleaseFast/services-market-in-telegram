export type ProjectStatus =
  | "draft"
  | "open"
  | "in_progress"
  | "completed"
  | "archived"
  | "canceled";

export interface Project {
  id: string;
  customer_id: string;
  title: string;
  description: string;
  budget: string;
  currency: string;
  deadline: string | null;
  status: ProjectStatus;
  selected_specialist_id: string | null;
  template_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectTemplate {
  id: string;
  title: string;
  category: string;
  description_template: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Application {
  id: string;
  project_id: string;
  specialist_id: string;
  cover_letter: string | null;
  status: "pending" | "accepted" | "rejected" | "withdrawn";
  created_at: string;
}

export interface SpecialistProfile {
  id: string;
  user_id: string;
  full_name: string;
  age: number;
  category: string;
  years_experience: number;
  bio: string;
  avatar_url: string | null;
  rating_avg: string;
  rating_count: number;
  workplaces: { id: string; title: string; company: string; period: string | null }[];
  portfolio_links: { id: string; url: string; label: string | null }[];
}
