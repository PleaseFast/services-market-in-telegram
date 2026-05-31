import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/avatar/Avatar";
import { usePublicSpecialist } from "@/features/specialist/api";
import { ServicesBlock } from "@/features/specialist/components/services/ServicesBlock";
import { ReviewsBlock } from "@/features/specialist/components/reviews/ReviewsBlock";
import { StarRating } from "@/features/specialist/components/reviews/StarRating";
import { categoryLabel } from "@/lib/categories";
import type { TimelineItem } from "@/features/projects/types";

function useYearsRange() {
  const { t } = useTranslation();
  return (item: TimelineItem): string => {
    if (item.is_current) return t("specialist.public.yearsRangePresent", { start: item.start_year });
    if (item.end_year === null) return `${item.start_year}`;
    if (item.start_year === item.end_year) return `${item.start_year}`;
    return `${item.start_year} – ${item.end_year}`;
  };
}

function ReadOnlyTimelineList({
  items,
  emptyLabel,
}: {
  items: TimelineItem[];
  emptyLabel: string;
}) {
  const yearsRange = useYearsRange();
  if (!items || items.length === 0) {
    return <p className="text-sm text-muted-foreground italic">{emptyLabel}</p>;
  }
  const sorted = [...items].sort((a, b) => a.position - b.position);
  return (
    <div className="space-y-3">
      {sorted.map((it) => (
        <div key={it.id} className="border-l-2 border-muted pl-4 py-1">
          <p className="font-medium leading-tight">{it.title}</p>
          <p className="text-xs text-muted-foreground mt-0.5">{yearsRange(it)}</p>
          {it.description && (
            <p className="text-sm text-muted-foreground whitespace-pre-line mt-1">
              {it.description}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

export function SpecialistProfilePublicPage() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const { data: profile, isLoading, error } = usePublicSpecialist(id);

  if (isLoading) return <p className="text-muted-foreground text-sm">{t("specialist.public.loading")}</p>;
  if (error || !profile) {
    return (
      <p className="text-muted-foreground text-sm">{t("specialist.public.notFound")}</p>
    );
  }

  const ratingAvg = Number(profile.rating_avg ?? 0);

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start gap-4 flex-wrap sm:flex-nowrap">
            <Avatar avatarId={profile.avatar_id} size="xl" />
            <div className="min-w-0 space-y-2 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
                  {profile.full_name}
                </h1>
                {(profile.categories ?? []).map((c) => (
                  <Badge key={c} tone="outline">
                    {categoryLabel(c)}
                  </Badge>
                ))}
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <StarRating value={ratingAvg} />
                <span className="text-sm text-muted-foreground">
                  {profile.rating_count > 0
                    ? t("specialist.public.reviewsCount", {
                        count: profile.rating_count,
                        value: ratingAvg.toFixed(2),
                      })
                    : t("specialist.reviews.empty")}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                {t("specialist.public.yearsExperience", { years: profile.years_experience })}
              </p>
            </div>
          </div>
          {profile.bio && (
            <p className="text-sm text-muted-foreground whitespace-pre-line mt-6">{profile.bio}</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("specialist.public.servicesTitle")}</CardTitle>
        </CardHeader>
        <CardContent>
          <ServicesBlock services={profile.services} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("specialist.public.experienceTitle")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <section className="space-y-2">
            <h3 className="text-sm font-semibold">{t("specialist.public.work")}</h3>
            <ReadOnlyTimelineList
              items={profile.timeline.work}
              emptyLabel={t("specialist.public.emptyWork")}
            />
          </section>
          <section className="space-y-2">
            <h3 className="text-sm font-semibold">{t("specialist.public.education")}</h3>
            <ReadOnlyTimelineList
              items={profile.timeline.education}
              emptyLabel={t("specialist.public.emptyEducation")}
            />
          </section>
          <section className="space-y-2">
            <h3 className="text-sm font-semibold">{t("specialist.public.achievements")}</h3>
            <ReadOnlyTimelineList
              items={profile.timeline.achievement}
              emptyLabel={t("specialist.public.emptyAchievements")}
            />
          </section>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <ReviewsBlock
            userId={profile.user_id}
            ratingAvg={ratingAvg}
            ratingCount={profile.rating_count}
          />
        </CardContent>
      </Card>
    </div>
  );
}
