import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { http } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Avatar } from "@/components/avatar/Avatar";
import { CATEGORIES } from "@/lib/categories";
import type { Page, SpecialistProfile } from "@/features/projects/types";

const RATING_OPTIONS: Array<{ label: string; value: string }> = [
  { label: "Any rating", value: "" },
  { label: "≥ 1★", value: "1" },
  { label: "≥ 2★", value: "2" },
  { label: "≥ 3★", value: "3" },
  { label: "≥ 4★", value: "4" },
  { label: "5★", value: "5" },
];

export function SpecialistsCatalog() {
  const [category, setCategory] = useState<string>("");
  const [minRating, setMinRating] = useState<string>("");

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
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Specialists</h1>
        <div className="flex items-center gap-2 flex-wrap">
          <Select
            className="rounded-xl"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            aria-label="Filter by category"
          >
            <option value="">Any category</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </Select>
          <Select
            className="rounded-xl"
            value={minRating}
            onChange={(e) => setMinRating(e.target.value)}
            aria-label="Filter by minimum rating"
          >
            {RATING_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </Select>
        </div>
      </div>
      {isLoading && <p className="text-muted-foreground text-sm">Loading…</p>}
      <div className="grid md:grid-cols-2 gap-4">
        {data?.items.map((s) => (
          <Link key={s.id} to={`/specialists/${s.user_id}`} className="block">
            <Card className="hover:border-foreground/30 transition-colors h-full">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <Avatar avatarId={s.avatar_id} size="md" />
                  <div className="min-w-0">
                    <CardTitle className="text-base font-medium">{s.full_name}</CardTitle>
                    <CardDescription>
                      {(s.categories ?? []).join(", ") || "—"} · {s.years_experience}y · ⭐{" "}
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
        ))}
        {data && data.items.length === 0 && (
          <p className="text-muted-foreground text-sm">No specialists match these filters.</p>
        )}
      </div>
    </div>
  );
}
