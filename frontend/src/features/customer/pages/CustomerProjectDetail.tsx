import { Link, useNavigate, useParams } from "react-router-dom";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/avatar/Avatar";
import {
  useApplicants,
  useArchiveProject,
  useCompleteProject,
  useDeleteProject,
  usePauseProject,
  useProject,
  usePublishProject,
  useResumeProject,
  useSelectSpecialist,
} from "@/features/projects/api";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import { LeaveReviewCard } from "@/features/projects/components/LeaveReviewCard";
import { useUserReviews } from "@/features/specialist/api";
import { StarRating } from "@/features/specialist/components/reviews/StarRating";
import { projectStatusLabel } from "@/lib/projectStatus";
import { categoryLabel } from "@/lib/categories";

export function CustomerProjectDetail() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: project } = useProject(id);
  const { data: applicants } = useApplicants(
    project && (project.status === "open" || project.status === "in_progress" || project.status === "completed")
      ? id
      : undefined,
  );
  const me = useAuthStore((s) => s.user);
  const reviewed = ["completed", "archived"].includes(project?.status ?? "");
  const { data: specialistReviews } = useUserReviews(
    reviewed && project?.selected_specialist_id ? project.selected_specialist_id : undefined,
  );
  const myReview = useMemo(
    () =>
      specialistReviews?.items.find(
        (r) => r.project_id === project?.id && r.author_id === me?.id,
      ),
    [specialistReviews, project?.id, me?.id],
  );
  const publish = usePublishProject();
  const select = useSelectSpecialist();
  const complete = useCompleteProject();
  const archive = useArchiveProject();
  const pause = usePauseProject();
  const resume = useResumeProject();
  const del = useDeleteProject();

  if (!project) return <p className="text-muted-foreground text-sm">{t("common.states.loading")}</p>;

  const canEdit = ["draft", "open", "paused"].includes(project.status);
  const canDelete = ["draft", "open", "paused", "canceled"].includes(project.status);

  const handleDelete = () => {
    if (!window.confirm(t("projects.confirmDelete"))) return;
    del.mutate(project.id, {
      onSuccess: () => navigate("/c/projects"),
    });
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start gap-2">
            <div>
              <CardTitle className="text-xl font-semibold tracking-tight">
                {project.title}
              </CardTitle>
              <CardDescription>
                {t("projects.labels.budgetDeadline", {
                  budget: project.budget,
                  currency: project.currency,
                  deadline: formatDate(project.deadline),
                })}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge tone="outline">{projectStatusLabel(project.status)}</Badge>
              {project.status === "paused" && (
                <Badge tone="outline" className="border-amber-500 text-amber-700">
                  {projectStatusLabel("paused")}
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{project.description}</p>
          <div className="flex flex-wrap gap-2">
            {project.status === "draft" && (
              <Button onClick={() => publish.mutate(project.id)} disabled={publish.isPending}>
                {t("projects.actions.publish")}
              </Button>
            )}
            {project.status === "open" && (
              <Button
                variant="outline"
                onClick={() => pause.mutate(project.id)}
                disabled={pause.isPending}
              >
                {t("projects.actions.pause")}
              </Button>
            )}
            {project.status === "paused" && (
              <Button
                onClick={() => resume.mutate(project.id)}
                disabled={resume.isPending}
              >
                {t("projects.actions.resume")}
              </Button>
            )}
            {canEdit && (
              <Button variant="outline" asChild>
                <Link to={`/c/projects/${project.id}/edit`}>{t("projects.actions.edit")}</Link>
              </Button>
            )}
            {project.status === "in_progress" && (
              <Button onClick={() => complete.mutate(project.id)} disabled={complete.isPending}>
                {t("projects.actions.complete")}
              </Button>
            )}
            {["completed", "canceled"].includes(project.status) && (
              <Button variant="outline" onClick={() => archive.mutate(project.id)} disabled={archive.isPending}>
                {t("projects.actions.archive")}
              </Button>
            )}
            {canDelete && (
              <Button
                variant="outline"
                className="text-destructive border-destructive/40 hover:bg-destructive/10"
                onClick={handleDelete}
                disabled={del.isPending}
              >
                {t("projects.actions.delete")}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {(project.status === "open" || project.status === "paused") && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium">
              {t("projects.labels.applicants", { count: applicants?.length ?? 0 })}
            </CardTitle>
            <CardDescription>{t("projects.labels.applicantsHint")}</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y">
              {applicants?.map((a) => {
                const cats = (a.specialist?.categories ?? []).map(categoryLabel).join(", ") || "—";
                const ratingText = a.specialist
                  ? t("projects.labels.ratingFormat", {
                      value: a.specialist.rating_avg.toFixed(2),
                      count: a.specialist.rating_count,
                    })
                  : t("projects.labels.noRating");
                return (
                  <li
                    key={a.id}
                    className="py-3 flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3"
                  >
                    <Link
                      to={`/specialists/${a.specialist_id}`}
                      className="flex items-start gap-3 flex-1 min-w-0 group"
                    >
                      <Avatar avatarId={a.specialist?.avatar_id} size="md" />
                      <div className="min-w-0">
                        <p className="font-medium group-hover:underline underline-offset-2">
                          {a.specialist?.full_name ?? t("projects.labels.anonymous")}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {cats} · {ratingText}
                        </p>
                        {a.cover_letter && (
                          <p className="text-sm text-muted-foreground whitespace-pre-wrap mt-1">
                            {a.cover_letter}
                          </p>
                        )}
                      </div>
                    </Link>
                    <Button
                      size="sm"
                      className="h-11 sm:h-9 self-start"
                      onClick={() =>
                        select.mutate({ projectId: project.id, specialistId: a.specialist_id })
                      }
                      disabled={select.isPending}
                    >
                      {t("projects.actions.select")}
                    </Button>
                  </li>
                );
              })}
              {applicants && applicants.length === 0 && (
                <li className="py-3 text-sm text-muted-foreground">{t("projects.labels.noApplicants")}</li>
              )}
            </ul>
          </CardContent>
        </Card>
      )}

      {reviewed && project.selected_specialist_id && !myReview && (
        <LeaveReviewCard projectId={project.id} subject="specialist" />
      )}
      {reviewed && project.selected_specialist_id && myReview && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium">{t("review.yourReview")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <StarRating value={myReview.rating} />
            {myReview.text && (
              <p className="text-sm text-muted-foreground whitespace-pre-line">{myReview.text}</p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
