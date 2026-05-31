import { useTranslation } from "react-i18next";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import { useUserReviews } from "@/features/specialist/api";
import { StarRating } from "./StarRating";

interface ReviewsBlockProps {
  userId: string;
  ratingAvg: number;
  ratingCount: number;
}

export function ReviewsBlock({ userId, ratingAvg, ratingCount }: ReviewsBlockProps) {
  const { t } = useTranslation();
  const { data, isLoading } = useUserReviews(userId);
  const items = data?.items ?? [];

  return (
    <section className="space-y-4">
      <div className="flex items-baseline gap-3 flex-wrap">
        <h3 className="text-base font-medium">{t("specialist.reviews.title")}</h3>
        <div className="flex items-center gap-2">
          <StarRating value={ratingAvg} />
          <span className="text-sm text-muted-foreground">
            {ratingCount > 0
              ? t("specialist.reviews.count", { count: ratingCount, value: ratingAvg.toFixed(2) })
              : t("specialist.reviews.empty")}
          </span>
        </div>
      </div>
      {isLoading && <p className="text-muted-foreground text-sm">{t("specialist.reviews.loading")}</p>}
      {!isLoading && items.length === 0 && (
        <p className="text-sm text-muted-foreground italic">{t("specialist.reviews.empty")}</p>
      )}
      <div className="space-y-3">
        {items.map((r) => (
          <Card key={r.id}>
            <CardContent className="p-4 space-y-2">
              <div className="flex items-start justify-between gap-2 flex-wrap">
                <div className="flex flex-col">
                  <p className="font-medium leading-tight">{r.project_title}</p>
                  <p className="text-xs text-muted-foreground">
                    {t("specialist.reviews.byAuthor", { author: r.author_name })}
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">{formatDate(r.created_at)}</p>
              </div>
              <StarRating value={r.rating} size="sm" />
              {r.text && (
                <p className="text-sm text-muted-foreground whitespace-pre-line">{r.text}</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
