import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { usePublicFeed } from "@/features/projects/api";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

export function ProjectFeed() {
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get("q") ?? "");
  const isGuest = useAuthStore((s) => s.isGuest);
  const { data, isLoading } = usePublicFeed(q || undefined);

  // Keep ?q in the URL synced (debounced via blur for now — cheap).
  useEffect(() => {
    const urlQ = params.get("q") ?? "";
    if (urlQ !== q) {
      const next = new URLSearchParams(params);
      if (q) next.set("q", q);
      else next.delete("q");
      setParams(next, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
          {isGuest ? "Browse open projects" : "Open projects"}
        </h1>
        <Input
          placeholder="Filter by category…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs rounded-xl"
        />
      </div>
      {isLoading && <p className="text-muted-foreground text-sm">Loading…</p>}
      {data?.items.length === 0 && (
        <p className="text-muted-foreground text-sm">No open projects right now.</p>
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
                <div className="mt-3">
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
