import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { usePublicFeed, type FeedFilters, type FeedSort } from "@/features/projects/api";
import { useMyProfile } from "@/features/specialist/api";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import { projectStatusLabel } from "@/lib/projectStatus";
import { categoryLabel } from "@/lib/categories";

const SEARCH_DEBOUNCE_MS = 250;

function readFilters(params: URLSearchParams): FeedFilters {
  const q = params.get("q") ?? "";
  const sortRaw = params.get("sort");
  const sort: FeedSort = sortRaw === "viewed" ? "viewed" : "newest";
  const minRaw = params.get("budget_min");
  const maxRaw = params.get("budget_max");
  const budget_min = minRaw ? Number(minRaw) : undefined;
  const budget_max = maxRaw ? Number(maxRaw) : undefined;
  return {
    q: q || undefined,
    sort,
    budget_min: budget_min !== undefined && !Number.isNaN(budget_min) ? budget_min : undefined,
    budget_max: budget_max !== undefined && !Number.isNaN(budget_max) ? budget_max : undefined,
  };
}

function hasActiveFilters(f: FeedFilters): boolean {
  return Boolean(f.q || f.budget_min !== undefined || f.budget_max !== undefined || (f.sort && f.sort !== "newest"));
}

export function ProjectFeed() {
  const { t } = useTranslation();
  const [params, setParams] = useSearchParams();
  const isGuest = useAuthStore((s) => s.isGuest);
  const user = useAuthStore((s) => s.user);
  const isSpecialist = !!user && user.role === "specialist";
  const { data: profile } = useMyProfile();

  const filters = useMemo(() => readFilters(params), [params]);

  const [qInput, setQInput] = useState(filters.q ?? "");
  const [minInput, setMinInput] = useState(filters.budget_min?.toString() ?? "");
  const [maxInput, setMaxInput] = useState(filters.budget_max?.toString() ?? "");
  const [filtersOpen, setFiltersOpen] = useState(false);

  useEffect(() => {
    setQInput(filters.q ?? "");
    setMinInput(filters.budget_min?.toString() ?? "");
    setMaxInput(filters.budget_max?.toString() ?? "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  useEffect(() => {
    const tid = setTimeout(() => {
      const next = new URLSearchParams(params);
      if (qInput.trim()) next.set("q", qInput.trim());
      else next.delete("q");
      if (next.toString() !== params.toString()) setParams(next, { replace: true });
    }, SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(tid);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [qInput]);

  function commitBudget(key: "budget_min" | "budget_max", raw: string) {
    const next = new URLSearchParams(params);
    const num = Number(raw);
    if (raw && !Number.isNaN(num) && num >= 0) next.set(key, String(num));
    else next.delete(key);
    if (next.toString() !== params.toString()) setParams(next, { replace: true });
  }

  function setSort(sort: FeedSort) {
    const next = new URLSearchParams(params);
    if (sort === "newest") next.delete("sort");
    else next.set("sort", sort);
    if (next.toString() !== params.toString()) setParams(next, { replace: true });
  }

  function clearFilters() {
    setQInput("");
    setMinInput("");
    setMaxInput("");
    const next = new URLSearchParams(params);
    next.delete("q");
    next.delete("budget_min");
    next.delete("budget_max");
    next.delete("sort");
    setParams(next, { replace: true });
  }

  const { data, isLoading } = usePublicFeed(filters);
  const profileCategories = profile?.categories ?? [];
  const showScope = isSpecialist && !isGuest && profileCategories.length > 0;
  const scopeLabel = profileCategories.map(categoryLabel).join(", ");
  const active = hasActiveFilters(filters);

  const searchInput = (
    <Input
      placeholder={t("specialist.feed.searchPlaceholder")}
      value={qInput}
      onChange={(e) => setQInput(e.target.value)}
      className="rounded-xl"
    />
  );

  const budgetInputs = (
    <>
      <Input
        placeholder={t("specialist.feed.minBudget")}
        type="number"
        min={0}
        value={minInput}
        onChange={(e) => setMinInput(e.target.value)}
        onBlur={() => commitBudget("budget_min", minInput)}
        className="rounded-xl md:w-28"
        aria-label={t("specialist.feed.minBudgetAria")}
      />
      <Input
        placeholder={t("specialist.feed.maxBudget")}
        type="number"
        min={0}
        value={maxInput}
        onChange={(e) => setMaxInput(e.target.value)}
        onBlur={() => commitBudget("budget_max", maxInput)}
        className="rounded-xl md:w-28"
        aria-label={t("specialist.feed.maxBudgetAria")}
      />
    </>
  );

  const sortSelect = (
    <Select
      value={filters.sort ?? "newest"}
      onChange={(e) => setSort(e.target.value as FeedSort)}
      className="rounded-xl md:w-40"
      aria-label={t("specialist.feed.sortAria")}
    >
      <option value="newest">{t("specialist.feed.sortNewest")}</option>
      {isSpecialist && !isGuest && (
        <option value="viewed">{t("specialist.feed.sortViewed")}</option>
      )}
    </Select>
  );

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
          {isGuest ? t("specialist.feed.titleGuest") : t("specialist.feed.titleOpen")}
        </h1>
        {showScope && (
          <p className="text-sm text-muted-foreground">
            {t("specialist.feed.scope", { categories: scopeLabel })}
          </p>
        )}
      </div>

      <div className="space-y-3">
        <div className="flex gap-2 md:hidden">
          <div className="flex-1">{searchInput}</div>
          <Button
            type="button"
            variant="outline"
            onClick={() => setFiltersOpen((v) => !v)}
            aria-expanded={filtersOpen}
          >
            {t("specialist.feed.filters")}
          </Button>
        </div>
        <div className="hidden md:flex md:items-center md:gap-2">
          <div className="flex-1">{searchInput}</div>
          {budgetInputs}
          {sortSelect}
          {active && (
            <Button type="button" variant="ghost" size="sm" onClick={clearFilters}>
              {t("specialist.feed.clear")}
            </Button>
          )}
        </div>
        <div className={filtersOpen ? "flex flex-col gap-2 md:hidden" : "hidden"}>
          <div className="flex gap-2">{budgetInputs}</div>
          {sortSelect}
          {active && (
            <Button type="button" variant="ghost" size="sm" onClick={clearFilters}>
              {t("specialist.feed.clearAll")}
            </Button>
          )}
        </div>
      </div>

      {isLoading && <p className="text-muted-foreground text-sm">{t("common.states.loading")}</p>}
      {!isLoading && data?.items.length === 0 && (
        <p className="text-muted-foreground text-sm">
          {active
            ? t("specialist.feed.emptyFiltered")
            : showScope
              ? t("specialist.feed.emptyScoped", { categories: scopeLabel })
              : t("specialist.feed.emptyAll")}
        </p>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        {data?.items.map((p) => (
          <Link key={p.id} to={`/s/projects/${p.id}`}>
            <Card className="hover:border-foreground/30 transition-colors">
              <CardHeader>
                <CardTitle className="text-base font-medium">{p.title}</CardTitle>
                <CardDescription>
                  {t("projects.labels.budgetDeadline", {
                    budget: p.budget,
                    currency: p.currency,
                    deadline: formatDate(p.deadline),
                  })}
                </CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground line-clamp-3">
                {p.description}
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge tone="outline">{categoryLabel(p.category)}</Badge>
                  <Badge tone="outline">{projectStatusLabel(p.status)}</Badge>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
