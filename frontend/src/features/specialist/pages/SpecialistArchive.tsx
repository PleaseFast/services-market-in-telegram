import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useMySpecialistProjects } from "@/features/projects/api";

export function SpecialistArchive() {
  const { data } = useMySpecialistProjects();
  const archive = data?.items.filter((p) =>
    ["completed", "archived", "canceled"].includes(p.status),
  );

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Archive</h1>
      {archive?.length === 0 && <p className="text-muted-foreground text-sm">Nothing here yet.</p>}
      <div className="grid md:grid-cols-2 gap-4">
        {archive?.map((p) => (
          <Link to={`/s/projects/${p.id}`} key={p.id}>
            <Card>
              <CardHeader>
                <CardTitle>{p.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <Badge tone="outline">{p.status}</Badge>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
