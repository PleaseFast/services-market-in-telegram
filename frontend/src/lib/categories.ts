// Mirror of backend/app/core/categories.py. Keep both in sync. The closed
// vocabulary is intentional — it powers the specialist profile dropdown, the
// CreateProject form, and feed-side category scoping.

export const CATEGORIES = [
  "Frontend",
  "Backend",
  "Bots",
  "Mobile",
  "DevOps",
  "Data",
  "Design",
  "AI",
  "Other",
] as const;

export type Category = (typeof CATEGORIES)[number];

export const DEFAULT_CATEGORY: Category = "Other";

const _CATEGORY_SET = new Set<string>(CATEGORIES);

export function isCategory(value: unknown): value is Category {
  return typeof value === "string" && _CATEGORY_SET.has(value);
}

export function clampCategory(value: string | null | undefined): Category {
  return isCategory(value) ? value : DEFAULT_CATEGORY;
}

// Keyword tables must stay aligned with backend/app/core/categories.py KEYWORDS.
// Matching is plain lowercase-substring on `title + " " + description`.
const KEYWORDS: Record<Exclude<Category, "Other">, readonly string[]> = {
  Bots: ["telegram bot", "aiogram", "chatbot", "bot", "discord bot", "whatsapp bot", "slack bot"],
  Frontend: [
    "react",
    "next.js",
    "nextjs",
    "vue",
    "svelte",
    "tailwind",
    "spa",
    "dashboard",
    "landing page",
    "frontend",
    "front-end",
    "ui ",
    "web ui",
  ],
  Backend: [
    "fastapi",
    "django",
    "flask",
    "node.js",
    "nodejs",
    "express",
    "stripe",
    "rest api",
    "graphql",
    "postgres",
    "mysql",
    "backend",
    "back-end",
    "microservice",
    " api",
  ],
  Mobile: ["ios", "android", "react native", "flutter", "swift", "kotlin", "mobile app"],
  DevOps: [
    "docker",
    "kubernetes",
    "k8s",
    "ci/cd",
    "terraform",
    "ansible",
    "aws",
    "gcp",
    "azure",
    "devops",
    "infrastructure",
  ],
  Data: [
    "etl",
    "airflow",
    "snowflake",
    "bigquery",
    "redshift",
    "data pipeline",
    "analytics",
    "data warehouse",
    "spark",
  ],
  Design: [
    "figma",
    "logo",
    "ui kit",
    "branding",
    "illustration",
    "design system",
    "ux design",
    "visual design",
  ],
  AI: [
    "llm",
    "openai",
    "gpt",
    "claude",
    "anthropic",
    "rag",
    "ai chatbot",
    "machine learning",
    "ml model",
    "embedding",
    "vector db",
  ],
};

export function suggestCategory(title: string, description = ""): Category {
  const text = `${title ?? ""} ${description ?? ""}`.toLowerCase();
  if (!text.trim()) return DEFAULT_CATEGORY;

  let best: Category = DEFAULT_CATEGORY;
  let bestScore = 0;
  // Order matters: ties are broken by CATEGORIES declaration order, matching
  // the backend implementation.
  for (const category of CATEGORIES) {
    if (category === "Other") continue;
    const keywords = KEYWORDS[category];
    let score = 0;
    for (const kw of keywords) if (text.includes(kw)) score += 1;
    if (score > bestScore) {
      bestScore = score;
      best = category;
    }
  }
  return best;
}
