import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useMyCustomerProjects } from "@/features/projects/api";
import { projectStatusLabel } from "@/lib/projectStatus";

export function CustomerDashboard() {
  const { t } = useTranslation();
  const { data } = useMyCustomerProjects();
  const drafts = data?.items.filter((p) => p.status === "draft") ?? [];
  const open = data?.items.filter((p) => p.status === "open") ?? [];
  const active = data?.items.filter((p) => p.status === "in_progress") ?? [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
          {t("customer.dashboard.welcome")}
        </h1>
        <Button asChild>
          <Link to="/c/new">{t("customer.dashboard.newProject")}</Link>
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <SummaryCard title={t("customer.dashboard.summary.drafts")} count={drafts.length} link="/c/projects" />
        <SummaryCard title={t("customer.dashboard.summary.open")} count={open.length} link="/c/projects" />
        <SummaryCard title={t("customer.dashboard.summary.inProgress")} count={active.length} link="/c/projects" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("customer.dashboard.recent")}</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="divide-y">
            {data?.items.slice(0, 6).map((p) => (
              <li key={p.id} className="py-3 flex items-center justify-between">
                <Link to={`/c/projects/${p.id}`} className="hover:underline">
                  {p.title}
                </Link>
                <Badge tone={statusTone(p.status)}>{projectStatusLabel(p.status)}</Badge>
              </li>
            ))}
            {data && data.items.length === 0 && (
              <li className="py-6 text-center text-muted-foreground text-sm">
                {t("customer.dashboard.empty")}
              </li>
            )}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

function SummaryCard({ title, count, link }: { title: string; count: number; link: string }) {
  const { t } = useTranslation();
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <CardDescription>
          <Link to={link} className="hover:text-foreground hover:underline underline-offset-4">
            {t("customer.dashboard.viewAll")}
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
