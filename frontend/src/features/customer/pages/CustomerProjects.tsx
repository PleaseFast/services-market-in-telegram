import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useMyCustomerProjects } from "@/features/projects/api";

export function CustomerProjects() {
  const { data, isLoading } = useMyCustomerProjects();

  if (isLoading) return <p className="text-muted-foreground text-sm">Loading…</p>;
  return (
    <div className="space-y-6">
      <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">My projects</h1>
      <div className="grid md:grid-cols-2 gap-4">
        {data?.items.map((p) => (
          <Link to={`/c/projects/${p.id}`} key={p.id}>
            <Card className="hover:border-foreground/30 transition-colors">
              <CardHeader>
                <CardTitle className="text-base font-medium">{p.title}</CardTitle>
              </CardHeader>
              <CardContent className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">
                  {p.budget} {p.currency}
                </span>
                <Badge tone="outline">{p.status}</Badge>
              </CardContent>
            </Card>
          </Link>
        ))}
        {data && data.items.length === 0 && (
          <p className="text-muted-foreground text-sm">
            No projects yet.{" "}
            <Link to="/c/new" className="text-foreground underline underline-offset-4">
              Create one
            </Link>
            .
          </p>
        )}
      </div>
    </div>
  );
}
