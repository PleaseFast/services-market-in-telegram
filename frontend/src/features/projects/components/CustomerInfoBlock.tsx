import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar } from "@/components/avatar/Avatar";
import { StarRating } from "@/features/specialist/components/reviews/StarRating";
import { useUserReviews } from "@/features/specialist/api";
import { useCustomerOpenProjects, usePublicCustomer } from "@/features/customer/api";
import { formatDate } from "@/lib/utils";

interface CustomerInfoBlockProps {
  customerId: string;
  /** Hide this id from the "other open projects" list when present. */
  currentProjectId?: string;
}

/**
 * Embedded read-only block describing the project's customer. Renders on
 * project detail pages so a viewer (typically a specialist or guest) can
 * gauge the customer's reputation and see their other open work.
 *
 * There is intentionally no link from here to a standalone customer profile
 * page — customers don't have one. Everything a viewer needs sits inside
 * this block.
 */
export function CustomerInfoBlock({ customerId, currentProjectId }: CustomerInfoBlockProps) {
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
        <CardTitle className="text-base font-medium">About the customer</CardTitle>
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
                  ? `${ratingAvg.toFixed(2)} · ${ratingCount} ${ratingCount === 1 ? "review" : "reviews"}`
                  : "No reviews yet"}
              </span>
            </div>
          </div>
        </div>

        <section className="space-y-2">
          <h4 className="text-sm font-medium">Reviews</h4>
          {reviewsLoading && (
            <p className="text-sm text-muted-foreground">Loading…</p>
          )}
          {!reviewsLoading && reviews.length === 0 && (
            <p className="text-sm text-muted-foreground italic">No reviews yet.</p>
          )}
          <ul className="space-y-3">
            {reviews.map((r) => (
              <li key={r.id} className="rounded-lg border p-3 space-y-1.5">
                <div className="flex items-start justify-between gap-2 flex-wrap">
                  <div className="flex flex-col">
                    <p className="text-sm font-medium leading-tight">{r.project_title}</p>
                    <p className="text-xs text-muted-foreground">by {r.author_name}</p>
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
          <h4 className="text-sm font-medium">Other open projects from this customer</h4>
          {otherOpen.length === 0 && (
            <p className="text-sm text-muted-foreground italic">
              No other open projects right now.
            </p>
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
                      Deadline: {formatDate(p.deadline)}
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
