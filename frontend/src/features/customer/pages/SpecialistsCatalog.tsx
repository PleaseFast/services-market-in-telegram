import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { http } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Avatar } from "@/components/avatar/Avatar";
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
    <div className="space-y-6">
      <div className="flex justify-between items-center flex-wrap gap-3">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Specialists</h1>
        <Input
          className="max-w-xs rounded-xl"
          placeholder="Filter by category…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
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
                      {s.category} · {s.years_experience}y · ⭐ {Number(s.rating_avg).toFixed(2)} ({s.rating_count})
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
          <p className="text-muted-foreground text-sm">No specialists found.</p>
        )}
      </div>
    </div>
  );
}
