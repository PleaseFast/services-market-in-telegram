export type ProjectStatus =
  | "draft"
  | "open"
  | "paused"
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
  category: string;
  selected_specialist_id: string | null;
  template_id: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
  higher_rated_applicants?: number | null;
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

export interface SpecialistPreview {
  user_id: string;
  full_name: string;
  avatar_id: string;
  categories: string[];
  rating_avg: number;
  rating_count: number;
}

export interface Application {
  id: string;
  project_id: string;
  specialist_id: string;
  cover_letter: string | null;
  status: "pending" | "accepted" | "rejected" | "withdrawn";
  created_at: string;
  specialist?: SpecialistPreview | null;
}

export type TimelineKind = "work" | "education" | "achievement";

export interface TimelineItem {
  id: string;
  profile_id: string;
  kind: TimelineKind;
  title: string;
  description: string;
  start_year: number;
  end_year: number | null;
  is_current: boolean;
  position: number;
}

export interface SpecialistService {
  service_id: string;
  slug: string;
  category: string;
  subcategory: string;
  label: string;
  price_amount: string;
  price_currency: string;
  position: number;
}

export interface ServiceCatalogItem {
  id: string;
  slug: string;
  category: string;
  subcategory: string;
  label: string;
  position: number;
}

export interface SpecialistProfile {
  id: string;
  user_id: string;
  full_name: string;
  age: number;
  categories: string[];
  years_experience: number;
  bio: string;
  avatar_id: string;
  rating_avg: string;
  rating_count: number;
  timeline: {
    work: TimelineItem[];
    education: TimelineItem[];
    achievement: TimelineItem[];
  };
  services: SpecialistService[];
}

export interface Review {
  id: string;
  project_id: string;
  project_title: string;
  author_id: string;
  author_name: string;
  subject_id: string;
  rating: number;
  text: string | null;
  created_at: string;
}

export interface CustomerPublic {
  id: string;
  user_id: string;
  display_name: string;
  avatar_id: string;
  rating_avg: string;
  rating_count: number;
}
