import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useMyCustomerProjects } from "@/features/projects/api";

export function CustomerDashboard() {
  const { data } = useMyCustomerProjects();
  const drafts = data?.items.filter((p) => p.status === "draft") ?? [];
  const open = data?.items.filter((p) => p.status === "open") ?? [];
  const active = data?.items.filter((p) => p.status === "in_progress") ?? [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Welcome back</h1>
        <Button asChild>
          <Link to="/c/new">+ New project</Link>
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <SummaryCard title="Drafts" count={drafts.length} link="/c/projects" />
        <SummaryCard title="Open" count={open.length} link="/c/projects" />
        <SummaryCard title="In progress" count={active.length} link="/c/projects" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Recent</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="divide-y">
            {data?.items.slice(0, 6).map((p) => (
              <li key={p.id} className="py-3 flex items-center justify-between">
                <Link to={`/c/projects/${p.id}`} className="hover:underline">
                  {p.title}
                </Link>
                <Badge tone={statusTone(p.status)}>{p.status}</Badge>
              </li>
            ))}
            {data && data.items.length === 0 && (
              <li className="py-6 text-center text-muted-foreground text-sm">
                No projects yet — create your first one.
              </li>
            )}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

function SummaryCard({ title, count, link }: { title: string; count: number; link: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <CardDescription>
          <Link to={link} className="hover:text-foreground hover:underline underline-offset-4">
            View all
          </Link>
        </CardDescription>
      </CardHeader>
      <CardContent className="text-3xl font-semibold tracking-tight">{count}</CardContent>
    </Card>
  );
}

function statusTone(s: string): "default" | "primary" | "success" | "warning" | "outline" {
  if (s === "open") return "outline";
  if (s === "in_progress") return "success";
  if (s === "completed") return "success";
  if (s === "draft") return "warning";
  return "outline";
}
