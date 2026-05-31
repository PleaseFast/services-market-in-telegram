import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar } from "@/components/avatar/Avatar";
import { StarRating } from "@/features/specialist/components/reviews/StarRating";
import { useUserReviews } from "@/features/specialist/api";
import { useCustomerOpenProjects, usePublicCustomer } from "@/features/customer/api";
import { formatDate } from "@/lib/utils";

interface CustomerInfoBlockProps {
  customerId: string;
  currentProjectId?: string;
}

export function CustomerInfoBlock({ customerId, currentProjectId }: CustomerInfoBlockProps) {
  const { t } = useTranslation();
  const { data: customer } = usePublicCustomer(customerId);
  const { data: reviewsPage, isLoading: reviewsLoading } = useUserReviews(customerId);
  const { data: openProjects } = useCustomerOpenProjects(customerId);

  if (!customer) {
    return null;
  }

  const ratingAvg = Number(customer.rating_avg);
  const ratingCount = customer.rating_count;
  const reviews = reviewsPage?.items ?? [];
  const otherOpen = (openProjects ?? []).filter((p) => p.id !== currentProjectId);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">{t("customerInfo.title")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="flex items-start gap-3">
          <Avatar avatarId={customer.avatar_id} size="md" />
          <div className="min-w-0">
            <p className="font-medium leading-tight">{customer.display_name}</p>
            <div className="flex items-center gap-2 mt-1">
              <StarRating value={ratingAvg} size="sm" />
              <span className="text-xs text-muted-foreground">
                {ratingCount > 0
                  ? t("customerInfo.reviewsCount", {
                      count: ratingCount,
                      value: ratingAvg.toFixed(2),
                    })
                  : t("customerInfo.noReviews")}
              </span>
            </div>
          </div>
        </div>

        <section className="space-y-2">
          <h4 className="text-sm font-medium">{t("customerInfo.reviews")}</h4>
          {reviewsLoading && (
            <p className="text-sm text-muted-foreground">{t("customerInfo.reviewsLoading")}</p>
          )}
          {!reviewsLoading && reviews.length === 0 && (
            <p className="text-sm text-muted-foreground italic">{t("customerInfo.noReviews")}</p>
          )}
          <ul className="space-y-3">
            {reviews.map((r) => (
              <li key={r.id} className="rounded-lg border p-3 space-y-1.5">
                <div className="flex items-start justify-between gap-2 flex-wrap">
                  <div className="flex flex-col">
                    <p className="text-sm font-medium leading-tight">{r.project_title}</p>
                    <p className="text-xs text-muted-foreground">
                      {t("customerInfo.byAuthor", { author: r.author_name })}
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">{formatDate(r.created_at)}</p>
                </div>
                <StarRating value={r.rating} size="sm" />
                {r.text && (
                  <p className="text-sm text-muted-foreground whitespace-pre-line">{r.text}</p>
                )}
              </li>
            ))}
          </ul>
        </section>

        <section className="space-y-2">
          <h4 className="text-sm font-medium">{t("customerInfo.otherOpen")}</h4>
          {otherOpen.length === 0 && (
            <p className="text-sm text-muted-foreground italic">{t("customerInfo.noOtherOpen")}</p>
          )}
          <ul className="space-y-2">
            {otherOpen.map((p) => (
              <li key={p.id}>
                <Link
                  to={`/s/projects/${p.id}`}
                  className="block rounded-lg border p-3 hover:bg-muted/40 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2 flex-wrap">
                    <p className="text-sm font-medium leading-tight">{p.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {p.budget} {p.currency}
                    </p>
                  </div>
                  {p.deadline && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {t("customerInfo.deadlinePrefix", { date: formatDate(p.deadline) })}
                    </p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </CardContent>
    </Card>
  );
}
