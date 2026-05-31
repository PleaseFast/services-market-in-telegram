import { useParams } from "react-router-dom";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useApply, useProject } from "@/features/projects/api";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import { GuestPrompt } from "@/components/GuestPrompt";
import { CustomerInfoBlock } from "@/features/projects/components/CustomerInfoBlock";
import { LeaveReviewCard } from "@/features/projects/components/LeaveReviewCard";
import { useUserReviews } from "@/features/specialist/api";
import { StarRating } from "@/features/specialist/components/reviews/StarRating";
import { projectStatusLabel } from "@/lib/projectStatus";
import { ApiError } from "@/lib/api";

export function ProjectDetailSpecialist() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const { data: project, isLoading } = useProject(id);
  const apply = useApply();
  const [cover, setCover] = useState("");
  const [done, setDone] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const isGuest = useAuthStore((s) => s.isGuest);
  const me = useAuthStore((s) => s.user);

  const reviewed = ["completed", "archived"].includes(project?.status ?? "");
  const isSelectedSpecialist =
    !!project && !isGuest && !!me && me.id === project.selected_specialist_id;

  const { data: customerReviews } = useUserReviews(
    reviewed && isSelectedSpecialist ? project?.customer_id : undefined,
  );
  const myReview = useMemo(
    () =>
      customerReviews?.items.find(
        (r) => r.project_id === project?.id && r.author_id === me?.id,
      ),
    [customerReviews, project?.id, me?.id],
  );

  if (isLoading) return <p className="text-muted-foreground text-sm">{t("common.states.loading")}</p>;
  if (!project) return <p>{t("specialist.detail.notFound")}</p>;

  const publishedDisplay = formatDate(project.published_at ?? project.created_at);
  const higher = project.higher_rated_applicants ?? 0;

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
              <p className="text-xs text-muted-foreground mt-1">
                {t("specialist.detail.publishedPrefix", { date: publishedDisplay })}
              </p>
            </div>
            <Badge tone="outline">{projectStatusLabel(project.status)}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {higher > 0 && (
            <p className="text-xs rounded-md border border-amber-500/40 bg-amber-50 text-amber-800 px-3 py-2">
              {t("specialist.detail.higherRated", { count: higher })}
            </p>
          )}
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{project.description}</p>
        </CardContent>
      </Card>

      <CustomerInfoBlock customerId={project.customer_id} currentProjectId={project.id} />

      {isGuest && project.status === "open" && <GuestPrompt actionKey="apply" />}

      {!isGuest && project.status === "open" && !done && (
        <Card>
          <CardHeader>
            <CardTitle>{t("specialist.detail.applyTitle")}</CardTitle>
            <CardDescription>{t("specialist.detail.applyHint")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              rows={5}
              value={cover}
              onChange={(e) => setCover(e.target.value)}
              placeholder={t("specialist.detail.coverLetterPlaceholder")}
            />
            {err && <p className="text-sm text-destructive">{err}</p>}
            <Button
              disabled={apply.isPending}
              onClick={async () => {
                setErr(null);
                try {
                  await apply.mutateAsync({ projectId: project.id, coverLetter: cover || undefined });
                  setDone(true);
                } catch (e: unknown) {
                  const message =
                    e instanceof ApiError ? e.localized() : (e as Error).message;
                  setErr(message);
                }
              }}
            >
              {apply.isPending ? t("specialist.detail.submitting") : t("specialist.detail.submit")}
            </Button>
          </CardContent>
        </Card>
      )}

      {done && (
        <Card>
          <CardContent className="pt-6">{t("specialist.detail.applicationSent")}</CardContent>
        </Card>
      )}

      {reviewed && isSelectedSpecialist && !myReview && (
        <LeaveReviewCard projectId={project.id} subject="customer" />
      )}
      {reviewed && isSelectedSpecialist && myReview && (
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
