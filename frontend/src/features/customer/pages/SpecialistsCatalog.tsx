import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { http } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import type { Page, SpecialistProfile } from "@/features/projects/types";

export function SpecialistsCatalog() {
  const [q, setQ] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["specialists", q],
    queryFn: () =>
      http.get<Page<SpecialistProfile>>(
        `/specialists?limit=50${q ? `&category=${encodeURIComponent(q)}` : ""}`,
      ),
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Specialists</h1>
        <Input
          className="max-w-xs"
          placeholder="Filter by category…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>
      {isLoading && <p className="text-muted-foreground text-sm">Loading…</p>}
      <div className="grid md:grid-cols-2 gap-4">
        {data?.items.map((s) => (
          <Card key={s.id}>
            <CardHeader>
              <CardTitle>{s.full_name}</CardTitle>
              <CardDescription>
                {s.category} · {s.years_experience}y · ⭐ {Number(s.rating_avg).toFixed(2)} ({s.rating_count})
              </CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground line-clamp-3">{s.bio}</CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
