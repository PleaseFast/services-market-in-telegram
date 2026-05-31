import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useMyCustomerProjects } from "@/features/projects/api";
import { projectStatusLabel } from "@/lib/projectStatus";

export function CustomerProjects() {
  const { t } = useTranslation();
  const { data, isLoading } = useMyCustomerProjects();

  if (isLoading) return <p className="text-muted-foreground text-sm">{t("common.states.loading")}</p>;
  return (
    <div className="space-y-6">
      <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
        {t("customer.projects.title")}
      </h1>
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
                <div className="flex items-center gap-2">
                  {p.status === "paused" && (
                    <Badge tone="outline" className="border-amber-500 text-amber-700">
                      {projectStatusLabel("paused")}
                    </Badge>
                  )}
                  <Badge tone="outline">{projectStatusLabel(p.status)}</Badge>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
        {data && data.items.length === 0 && (
          <p className="text-muted-foreground text-sm">
            {t("customer.projects.empty")}{" "}
            <Link to="/c/new" className="text-foreground underline underline-offset-4">
              {t("customer.projects.createOne")}
            </Link>
            .
          </p>
        )}
      </div>
    </div>
  );
}
