import { useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { usePublicFeed } from "@/features/projects/api";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

export function ProjectFeed() {
  const [q, setQ] = useState("");
  const { data, isLoading } = usePublicFeed(q || undefined);
  const isGuest = useAuthStore((s) => s.isGuest);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">
          {isGuest ? "Browse open projects" : "Open projects"}
        </h1>
        <Input
          placeholder="Filter by category…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
      </div>
      {isLoading && <p className="text-muted-foreground text-sm">Loading…</p>}
      {data?.items.length === 0 && (
        <p className="text-muted-foreground text-sm">No open projects right now.</p>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        {data?.items.map((p) => (
          <Link key={p.id} to={`/s/projects/${p.id}`}>
            <Card className="hover:shadow-md transition">
              <CardHeader>
                <CardTitle>{p.title}</CardTitle>
                <CardDescription>
                  Budget: {p.budget} {p.currency} · Deadline: {formatDate(p.deadline)}
                </CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground line-clamp-3">
                {p.description}
                <div className="mt-3"><Badge tone="primary">{p.status}</Badge></div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
