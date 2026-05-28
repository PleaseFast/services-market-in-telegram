import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/avatar/Avatar";
import { usePublicSpecialist } from "@/features/specialist/api";
import { ServicesBlock } from "@/features/specialist/components/services/ServicesBlock";
import { ReviewsBlock } from "@/features/specialist/components/reviews/ReviewsBlock";
import { StarRating } from "@/features/specialist/components/reviews/StarRating";
import type { TimelineItem } from "@/features/projects/types";

function yearsRange(item: TimelineItem): string {
  if (item.is_current) return `${item.start_year} – present`;
  if (item.end_year === null) return `${item.start_year}`;
  if (item.start_year === item.end_year) return `${item.start_year}`;
  return `${item.start_year} – ${item.end_year}`;
}

function ReadOnlyTimelineList({
  items,
  emptyLabel,
}: {
  items: TimelineItem[];
  emptyLabel: string;
}) {
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
  const { id } = useParams<{ id: string }>();
  const { data: profile, isLoading, error } = usePublicSpecialist(id);

  if (isLoading) return <p className="text-muted-foreground text-sm">Loading…</p>;
  if (error || !profile) {
    return (
      <p className="text-muted-foreground text-sm">
        We couldn&apos;t find this specialist.
      </p>
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
                <Badge tone="outline">{profile.category}</Badge>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <StarRating value={ratingAvg} />
                <span className="text-sm text-muted-foreground">
                  {ratingAvg.toFixed(2)} · {profile.rating_count}{" "}
                  {profile.rating_count === 1 ? "review" : "reviews"}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                {profile.years_experience}+ years experience
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
          <CardTitle className="text-base font-medium">Services and work conditions</CardTitle>
        </CardHeader>
        <CardContent>
          <ServicesBlock services={profile.services} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Education and experience</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Work experience</h3>
            <ReadOnlyTimelineList
              items={profile.timeline.work}
              emptyLabel="No work experience listed."
            />
          </section>
          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Education</h3>
            <ReadOnlyTimelineList
              items={profile.timeline.education}
              emptyLabel="No education listed."
            />
          </section>
          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Achievements</h3>
            <ReadOnlyTimelineList
              items={profile.timeline.achievement}
              emptyLabel="No achievements listed."
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
