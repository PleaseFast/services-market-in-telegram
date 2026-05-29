import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
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
  const [params, setParams] = useSearchParams();
  const isGuest = useAuthStore((s) => s.isGuest);
  const user = useAuthStore((s) => s.user);
  const isSpecialist = !!user && user.role === "specialist";
  const { data: profile } = useMyProfile();

  // URL params are the source of truth for filters.
  const filters = useMemo(() => readFilters(params), [params]);

  // Local mirror of the search input so we can debounce URL updates.
  const [qInput, setQInput] = useState(filters.q ?? "");
  // Local mirror of budget inputs (commit on blur).
  const [minInput, setMinInput] = useState(filters.budget_min?.toString() ?? "");
  const [maxInput, setMaxInput] = useState(filters.budget_max?.toString() ?? "");
  // Mobile inline filter panel toggle.
  const [filtersOpen, setFiltersOpen] = useState(false);

  // Re-sync local mirrors when the URL changes from elsewhere (back button, Clear).
  useEffect(() => {
    setQInput(filters.q ?? "");
    setMinInput(filters.budget_min?.toString() ?? "");
    setMaxInput(filters.budget_max?.toString() ?? "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  // Debounce q → URL.
  useEffect(() => {
    const t = setTimeout(() => {
      const next = new URLSearchParams(params);
      if (qInput.trim()) next.set("q", qInput.trim());
      else next.delete("q");
      if (next.toString() !== params.toString()) setParams(next, { replace: true });
    }, SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(t);
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
  const scopeLabel = profileCategories.join(", ");
  const active = hasActiveFilters(filters);

  const searchInput = (
    <Input
      placeholder="Search projects…"
      value={qInput}
      onChange={(e) => setQInput(e.target.value)}
      className="rounded-xl"
    />
  );

  const budgetInputs = (
    <>
      <Input
        placeholder="Min $"
        type="number"
        min={0}
        value={minInput}
        onChange={(e) => setMinInput(e.target.value)}
        onBlur={() => commitBudget("budget_min", minInput)}
        className="rounded-xl md:w-28"
        aria-label="Minimum budget"
      />
      <Input
        placeholder="Max $"
        type="number"
        min={0}
        value={maxInput}
        onChange={(e) => setMaxInput(e.target.value)}
        onBlur={() => commitBudget("budget_max", maxInput)}
        className="rounded-xl md:w-28"
        aria-label="Maximum budget"
      />
    </>
  );

  const sortSelect = (
    <Select
      value={filters.sort ?? "newest"}
      onChange={(e) => setSort(e.target.value as FeedSort)}
      className="rounded-xl md:w-40"
      aria-label="Sort"
    >
      <option value="newest">Newest first</option>
      {isSpecialist && !isGuest && <option value="viewed">Viewed first</option>}
    </Select>
  );

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
          {isGuest ? "Browse open projects" : "Open projects"}
        </h1>
        {showScope && (
          <p className="text-sm text-muted-foreground">
            Showing projects in: {scopeLabel} · update your profile to change categories
          </p>
        )}
      </div>

      {/* Toolbar: full row on desktop, search + Filters toggle on mobile. */}
      <div className="space-y-3">
        <div className="flex gap-2 md:hidden">
          <div className="flex-1">{searchInput}</div>
          <Button
            type="button"
            variant="outline"
            onClick={() => setFiltersOpen((v) => !v)}
            aria-expanded={filtersOpen}
          >
            Filters
          </Button>
        </div>
        <div className="hidden md:flex md:items-center md:gap-2">
          <div className="flex-1">{searchInput}</div>
          {budgetInputs}
          {sortSelect}
          {active && (
            <Button type="button" variant="ghost" size="sm" onClick={clearFilters}>
              Clear
            </Button>
          )}
        </div>
        {/* Mobile inline filter panel */}
        <div className={filtersOpen ? "flex flex-col gap-2 md:hidden" : "hidden"}>
          <div className="flex gap-2">{budgetInputs}</div>
          {sortSelect}
          {active && (
            <Button type="button" variant="ghost" size="sm" onClick={clearFilters}>
              Clear all filters
            </Button>
          )}
        </div>
      </div>

      {isLoading && <p className="text-muted-foreground text-sm">Loading…</p>}
      {!isLoading && data?.items.length === 0 && (
        <p className="text-muted-foreground text-sm">
          {active
            ? "No open projects match your filters."
            : showScope
              ? `No open projects in ${scopeLabel} right now.`
              : "No open projects right now."}
        </p>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        {data?.items.map((p) => (
          <Link key={p.id} to={`/s/projects/${p.id}`}>
            <Card className="hover:border-foreground/30 transition-colors">
              <CardHeader>
                <CardTitle className="text-base font-medium">{p.title}</CardTitle>
                <CardDescription>
                  Budget: {p.budget} {p.currency} · Deadline: {formatDate(p.deadline)}
                </CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground line-clamp-3">
                {p.description}
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge tone="outline">{p.category}</Badge>
                  <Badge tone="outline">{p.status}</Badge>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
