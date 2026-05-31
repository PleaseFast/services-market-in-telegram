import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useMySpecialistProjects } from "@/features/projects/api";
import { projectStatusLabel } from "@/lib/projectStatus";

export function SpecialistArchive() {
  const { t } = useTranslation();
  const { data } = useMySpecialistProjects();
  const archive = data?.items.filter((p) =>
    ["completed", "archived", "canceled"].includes(p.status),
  );

  return (
    <div className="space-y-6">
      <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
        {t("specialist.archive.title")}
      </h1>
      {archive?.length === 0 && (
        <p className="text-muted-foreground text-sm">{t("specialist.archive.empty")}</p>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        {archive?.map((p) => (
          <Link to={`/s/projects/${p.id}`} key={p.id}>
            <Card className="hover:border-foreground/30 transition-colors">
              <CardHeader>
                <CardTitle className="text-base font-medium">{p.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <Badge tone="outline">{projectStatusLabel(p.status)}</Badge>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
