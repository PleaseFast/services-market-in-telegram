// Mirror of backend/app/core/categories.py. Keep both in sync. The closed
// vocabulary is intentional — it powers the specialist profile dropdown, the
// CreateProject form, and feed-side category scoping.

import i18n from "@/i18n";

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

/** Localized display label for a category. Canonical IDs (English) travel
 * over the wire; this is for UI rendering only. */
export function categoryLabel(category: string): string {
  const id = clampCategory(category);
  const key = `categories.${id}`;
  const translated = i18n.t(key);
  return typeof translated === "string" && translated !== key ? translated : id;
}

// Keyword tables must stay aligned with backend/app/core/categories.py KEYWORDS.
// Matching is plain lowercase-substring on `title + " " + description`.
const KEYWORDS: Record<Exclude<Category, "Other">, readonly string[]> = {
  Bots: [
    "telegram bot",
    "aiogram",
    "chatbot",
    "bot",
    "discord bot",
    "whatsapp bot",
    "slack bot",
    "бот",
    "телеграм-бот",
    "телеграм бот",
    "чат-бот",
    "дискорд-бот",
    "вотсап-бот",
  ],
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
    "фронтенд",
    "фронт-энд",
    "лендинг",
    "верстка",
    "вёрстка",
    "интерфейс",
    "веб-интерфейс",
    "дашборд",
    "одностраничник",
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
    "бэкенд",
    "бек-энд",
    "сервер",
    "серверная часть",
    "микросервис",
    "апи",
  ],
  Mobile: [
    "ios",
    "android",
    "react native",
    "flutter",
    "swift",
    "kotlin",
    "mobile app",
    "мобильное приложение",
    "мобильная разработка",
    "андроид",
    "айос",
  ],
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
    "девопс",
    "инфраструктура",
    "кубернетес",
    "терраформ",
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
    "данные",
    "хранилище данных",
    "аналитика",
    "etl-пайплайн",
    "пайплайн данных",
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
    "дизайн",
    "фигма",
    "логотип",
    "айдентика",
    "брендинг",
    "иллюстрация",
    "ux-дизайн",
    "юай-кит",
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
    "ии",
    "искусственный интеллект",
    "машинное обучение",
    "нейросеть",
    "нейронн",
    "ллм",
    "эмбеддинг",
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
