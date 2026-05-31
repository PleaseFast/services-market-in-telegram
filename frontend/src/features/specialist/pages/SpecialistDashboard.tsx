import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar } from "@/components/avatar/Avatar";
import { useMyProfile } from "../api";
import { useMySpecialistProjects } from "@/features/projects/api";
import { categoryLabel } from "@/lib/categories";

export function SpecialistDashboard() {
  const { t } = useTranslation();
  const { data: profile } = useMyProfile();
  const { data: mine } = useMySpecialistProjects();

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        {profile && <Avatar avatarId={profile.avatar_id} size="lg" />}
        <div className="min-w-0">
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
            {t("specialist.dashboard.title")}
          </h1>
          {profile && (
            <p className="text-sm text-muted-foreground">
              {profile.full_name} · {(profile.categories ?? []).map(categoryLabel).join(", ") || "—"}
            </p>
          )}
        </div>
      </div>

      {profile === null && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium">
              {t("specialist.dashboard.finishProfile")}
            </CardTitle>
            <CardDescription>{t("specialist.dashboard.finishProfileHint")}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link to="/s/profile">{t("specialist.dashboard.createProfile")}</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("specialist.dashboard.browseProjects")}
            </CardTitle>
            <CardDescription>{t("specialist.dashboard.browseProjectsHint")}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link to="/s/feed">{t("specialist.dashboard.openFeed")}</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("specialist.dashboard.active")}
            </CardTitle>
            <CardDescription>
              {t("specialist.dashboard.engagedCount", { count: mine?.items.length ?? 0 })}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {mine?.items
                .filter((p) => p.status === "in_progress")
                .slice(0, 3)
                .map((p) => (
                  <li key={p.id}>
                    <Link to={`/s/projects/${p.id}`} className="hover:underline">
                      {p.title}
                    </Link>
                  </li>
                ))}
              {mine && mine.items.length === 0 && (
                <li className="text-muted-foreground">{t("specialist.dashboard.empty")}</li>
              )}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("specialist.dashboard.yourRating")}
            </CardTitle>
            <CardDescription>{t("specialist.dashboard.yourRatingHint")}</CardDescription>
          </CardHeader>
          <CardContent className="text-3xl font-semibold tracking-tight">
            {profile ? `${Number(profile.rating_avg).toFixed(2)} ★` : "—"}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
