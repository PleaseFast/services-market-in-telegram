import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { http } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Avatar } from "@/components/avatar/Avatar";
import { CATEGORIES, categoryLabel } from "@/lib/categories";
import type { Page, SpecialistProfile } from "@/features/projects/types";

export function SpecialistsCatalog() {
  const { t } = useTranslation();
  const [category, setCategory] = useState<string>("");
  const [minRating, setMinRating] = useState<string>("");

  const ratingOptions = useMemo(
    () => [
      { label: t("specialist.catalog.filters.anyRating"), value: "" },
      { label: t("specialist.catalog.filters.gte", { value: 1 }), value: "1" },
      { label: t("specialist.catalog.filters.gte", { value: 2 }), value: "2" },
      { label: t("specialist.catalog.filters.gte", { value: 3 }), value: "3" },
      { label: t("specialist.catalog.filters.gte", { value: 4 }), value: "4" },
      { label: t("specialist.catalog.filters.fiveStars"), value: "5" },
    ],
    [t],
  );

  const { data, isLoading } = useQuery({
    queryKey: ["specialists", category, minRating],
    queryFn: () => {
      const params = new URLSearchParams({ limit: "50" });
      if (category) params.set("category", category);
      if (minRating) params.set("min_rating", minRating);
      return http.get<Page<SpecialistProfile>>(`/specialists?${params.toString()}`);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center flex-wrap gap-3">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
          {t("specialist.catalog.title")}
        </h1>
        <div className="flex items-center gap-2 flex-wrap">
          <Select
            className="rounded-xl"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            aria-label={t("specialist.catalog.filters.categoryAria")}
          >
            <option value="">{t("specialist.catalog.filters.anyCategory")}</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {categoryLabel(c)}
              </option>
            ))}
          </Select>
          <Select
            className="rounded-xl"
            value={minRating}
            onChange={(e) => setMinRating(e.target.value)}
            aria-label={t("specialist.catalog.filters.ratingAria")}
          >
            {ratingOptions.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </Select>
        </div>
      </div>
      {isLoading && <p className="text-muted-foreground text-sm">{t("common.states.loading")}</p>}
      <div className="grid md:grid-cols-2 gap-4">
        {data?.items.map((s) => {
          const cats = (s.categories ?? []).map(categoryLabel).join(", ") || "—";
          return (
            <Link key={s.id} to={`/specialists/${s.user_id}`} className="block">
              <Card className="hover:border-foreground/30 transition-colors h-full">
                <CardHeader>
                  <div className="flex items-start gap-3">
                    <Avatar avatarId={s.avatar_id} size="md" />
                    <div className="min-w-0">
                      <CardTitle className="text-base font-medium">{s.full_name}</CardTitle>
                      <CardDescription>
                        {cats} · {t("specialist.catalog.yearsShort", { count: s.years_experience })} · ⭐{" "}
                        {Number(s.rating_avg).toFixed(2)} ({s.rating_count})
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground line-clamp-3">
                  {s.bio}
                </CardContent>
              </Card>
            </Link>
          );
        })}
        {data && data.items.length === 0 && (
          <p className="text-muted-foreground text-sm">{t("specialist.catalog.empty")}</p>
        )}
      </div>
    </div>
  );
}
