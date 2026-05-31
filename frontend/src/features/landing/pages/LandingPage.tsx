import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ArrowRight, BadgeCheck, MessageSquareText, Sparkles, Wallet } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/auth";
import { useTemplates, usePublicFeed } from "@/features/projects/api";
import { groupByCategory } from "@/lib/templates";
import { categoryLabel } from "@/lib/categories";
import { cn } from "@/lib/utils";

const FEATURE_KEYS = [
  { icon: MessageSquareText, key: "scope" },
  { icon: Wallet, key: "price" },
  { icon: BadgeCheck, key: "verified" },
  { icon: Sparkles, key: "reviews" },
] as const;

const LANDING_VISIBLE_PER_CATEGORY = 6;

export function LandingPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const { user } = useAuthStore();
  const { data: templates } = useTemplates();
  const { data: feed } = usePublicFeed();
  const [q, setQ] = useState("");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const grouped = useMemo(() => groupByCategory(templates ?? []), [templates]);
  const openProjectCount = feed?.total ?? 0;

  function submitSearch() {
    const trimmed = q.trim();
    nav(trimmed ? `/c/new?title=${encodeURIComponent(trimmed)}` : "/c/new");
  }

  return (
    <div className="space-y-20 pb-12">
      {/* HERO */}
      <section className="pt-12 md:pt-16 max-w-3xl">
        <h1 className="text-4xl md:text-6xl font-semibold tracking-tight leading-[1.05]">
          {t("landing.title")}
        </h1>
        <p className="mt-4 text-muted-foreground text-base md:text-lg">
          {openProjectCount > 0
            ? t("landing.openProjectsWithCount", { count: openProjectCount })
            : t("landing.noOpenProjects")}
        </p>

        <div className="mt-8 flex flex-col sm:flex-row gap-2 max-w-2xl">
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") submitSearch();
            }}
            placeholder={t("landing.search.placeholder")}
            className="h-12 text-base rounded-xl bg-muted/60 border-transparent focus-visible:bg-background"
          />
          <Button onClick={submitSearch} className="h-12 px-6 rounded-xl">
            {t("landing.search.submit")}
            <ArrowRight className="ml-1 h-4 w-4" />
          </Button>
        </div>

        <div className="mt-6 flex flex-wrap gap-3 items-center text-sm">
          {user ? (
            <Button asChild variant="outline">
              <Link to={user.role === "customer" ? "/c" : "/s"}>{t("landing.openDashboard")}</Link>
            </Button>
          ) : (
            <Link
              to="/register?role=specialist"
              className="text-muted-foreground hover:text-foreground underline-offset-4 hover:underline"
            >
              {t("landing.iAmSpecialist")}
            </Link>
          )}
        </div>
      </section>

      {/* FEATURES */}
      <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-10">
        {FEATURE_KEYS.map(({ icon: Icon, key }) => (
          <div key={key} className="space-y-3">
            <div className="h-10 w-10 flex items-center justify-center rounded-full bg-muted">
              <Icon className="h-5 w-5" />
            </div>
            <h3 className="font-medium">{t(`landing.features.${key}Title`)}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {t(`landing.features.${key}Body`)}
            </p>
          </div>
        ))}
      </section>

      {/* STATS */}
      <section className="text-sm text-muted-foreground">
        {openProjectCount > 0
          ? t("landing.stats.withCount", { count: openProjectCount })
          : t("landing.stats.empty")}
      </section>

      {/* CATEGORY GRID */}
      {grouped.length > 0 && (
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-10 gap-y-10">
          {grouped.map(({ category, items }) => {
            const isExpanded = expanded[category] ?? false;
            const visible = isExpanded ? items : items.slice(0, LANDING_VISIBLE_PER_CATEGORY);
            const hidden = items.length - visible.length;
            return (
              <div key={category} className="space-y-3">
                <div className="flex items-baseline gap-2">
                  <h3 className="font-semibold">{categoryLabel(category)}</h3>
                  <span className="text-xs text-muted-foreground">{items.length}</span>
                </div>
                <ul className="space-y-1.5">
                  {visible.map((tpl) => (
                    <li key={tpl.id}>
                      <Link
                        to={`/c/new?template_id=${tpl.id}`}
                        className={cn(
                          "text-sm text-muted-foreground hover:text-foreground",
                          "hover:underline underline-offset-4",
                        )}
                      >
                        {tpl.title}
                      </Link>
                    </li>
                  ))}
                </ul>
                {items.length > LANDING_VISIBLE_PER_CATEGORY && (
                  <button
                    type="button"
                    onClick={() => setExpanded((s) => ({ ...s, [category]: !isExpanded }))}
                    className="text-xs text-muted-foreground hover:text-foreground underline-offset-4 hover:underline"
                  >
                    {isExpanded
                      ? t("landing.category.showLess")
                      : t("landing.category.showMore", { count: hidden })}
                  </button>
                )}
              </div>
            );
          })}
        </section>
      )}
    </div>
  );
}
