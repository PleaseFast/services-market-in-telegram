// Mirror of backend/app/core/service_catalog.py.
// Used as a fallback when the backend catalog isn't fetched yet so the
// services editor can still render an immediate scaffolding. The live values
// from useServiceCatalog() take precedence at runtime.

export interface ServiceEntry {
  slug: string;
  category: string;
  subcategory: string;
  label: string;
}

function entries(category: string, subcategory: string, labels: string[]): ServiceEntry[] {
  return labels.map((label) => {
    const slugLabel = label
      .toLowerCase()
      .replace(/\//g, "-")
      .replace(/&/g, "and")
      .replace(/\+/g, "plus")
      .replace(/ /g, "-")
      .replace(/\(/g, "")
      .replace(/\)/g, "");
    return {
      slug: `${category.toLowerCase()}.${subcategory.toLowerCase().replace(/ /g, "-")}.${slugLabel}`,
      category,
      subcategory,
      label,
    };
  });
}

export const SERVICE_CATALOG: ServiceEntry[] = [
  ...entries("Design", "Web Design", [
    "Landing page design",
    "Chat UI design",
    "Dashboard UI design",
    "E-commerce storefront design",
    "Marketing site redesign",
  ]),
  ...entries("Design", "Graphic Design", [
    "Logo design",
    "Brand packaging",
    "Illustrations",
    "Social media kit",
  ]),
  ...entries("Design", "UX Design", [
    "User flows",
    "Wireframes",
    "Usability audit",
    "Design system documentation",
  ]),
  ...entries("Frontend", "Web Apps", [
    "SPA from scratch",
    "Migration to React",
    "Migration to Next.js",
    "Real-time UI",
  ]),
  ...entries("Frontend", "Landing Pages", [
    "Marketing landing page",
    "Pricing page",
    "Documentation site",
  ]),
  ...entries("Frontend", "Admin Dashboards", [
    "Admin panel",
    "Analytics dashboard",
    "Internal tools",
  ]),
  ...entries("Frontend", "Component Libraries", [
    "Design system kit",
    "Storybook setup",
    "Headless component library",
  ]),
  ...entries("Backend", "APIs", [
    "REST API",
    "GraphQL API",
    "WebSocket service",
    "API redesign",
  ]),
  ...entries("Backend", "Integrations", [
    "Stripe integration",
    "OpenAI integration",
    "Telegram integration",
    "Third-party CRM integration",
  ]),
  ...entries("Backend", "Auth", [
    "OAuth integration",
    "SSO setup",
    "Role-based access control",
  ]),
  ...entries("Backend", "Infrastructure", [
    "Database schema design",
    "Migrations and backfills",
    "Background job system",
  ]),
  ...entries("Bots", "Telegram Bots", [
    "Bot from scratch",
    "Aiogram FSM workflow",
    "Webhook integration",
    "Bot migration to aiogram 3",
  ]),
  ...entries("Bots", "Other Platforms", [
    "Discord bot",
    "Slack bot",
    "WhatsApp bot",
  ]),
  ...entries("Bots", "Bot Integrations", [
    "Payments inside bot",
    "Bot to CRM bridge",
    "Bot analytics",
  ]),
  ...entries("Mobile", "iOS", [
    "Native iOS app",
    "iOS app refactor",
    "App Store submission",
  ]),
  ...entries("Mobile", "Android", [
    "Native Android app",
    "Android app refactor",
    "Play Store submission",
  ]),
  ...entries("Mobile", "Cross-platform", [
    "React Native app",
    "Flutter app",
    "Hybrid web wrapper",
  ]),
  ...entries("DevOps", "CI and CD", [
    "GitHub Actions setup",
    "CI pipeline overhaul",
    "Release automation",
  ]),
  ...entries("DevOps", "Cloud", [
    "AWS setup",
    "GCP setup",
    "Cloud migration",
  ]),
  ...entries("DevOps", "Containers", [
    "Docker setup",
    "Kubernetes deployment",
    "Helm chart authoring",
  ]),
  ...entries("DevOps", "Infrastructure as Code", [
    "Terraform setup",
    "Ansible automation",
  ]),
  ...entries("DevOps", "Observability", [
    "Logging pipeline",
    "Metrics and alerting",
    "Tracing setup",
  ]),
  ...entries("Data", "Pipelines", [
    "ETL pipeline",
    "Airflow DAG authoring",
    "Streaming pipeline",
  ]),
  ...entries("Data", "Warehousing", [
    "Snowflake setup",
    "BigQuery setup",
    "Data warehouse migration",
  ]),
  ...entries("Data", "Analytics", [
    "Analytics dashboard",
    "Custom reporting",
    "Data audit",
  ]),
  ...entries("AI", "LLM Integration", [
    "OpenAI integration",
    "Anthropic integration",
    "Self-hosted LLM setup",
  ]),
  ...entries("AI", "RAG", [
    "Document RAG system",
    "Knowledge-base assistant",
    "Vector DB setup",
  ]),
  ...entries("AI", "ML Models", [
    "Model fine-tuning",
    "Embedding pipeline",
    "Recommendation engine",
  ]),
  ...entries("AI", "Conversational AI", [
    "AI chatbot",
    "Voice assistant",
  ]),
  ...entries("Other", "Consulting", [
    "Technical consulting",
    "Code review",
    "Architecture review",
  ]),
  ...entries("Other", "Mentoring", [
    "1:1 mentoring",
    "Team training",
  ]),
  ...entries("Other", "Writing", [
    "Technical writing",
    "API documentation",
  ]),
];

/** Group flat entries by (category, subcategory) preserving declaration order. */
export function groupCatalog(
  entries: { id?: string; slug: string; category: string; subcategory: string; label: string }[],
): { category: string; subcategories: { subcategory: string; items: typeof entries }[] }[] {
  const byCat = new Map<string, Map<string, typeof entries>>();
  for (const e of entries) {
    if (!byCat.has(e.category)) byCat.set(e.category, new Map());
    const subs = byCat.get(e.category)!;
    if (!subs.has(e.subcategory)) subs.set(e.subcategory, []);
    subs.get(e.subcategory)!.push(e);
  }
  return Array.from(byCat.entries()).map(([category, subs]) => ({
    category,
    subcategories: Array.from(subs.entries()).map(([subcategory, items]) => ({
      subcategory,
      items,
    })),
  }));
}
