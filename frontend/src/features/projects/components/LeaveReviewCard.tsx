import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { StarRatingInput } from "@/features/specialist/components/reviews/StarRatingInput";
import { StarRating } from "@/features/specialist/components/reviews/StarRating";
import { useCreateReview } from "@/features/projects/api";
import { ApiError } from "@/lib/api";

interface LeaveReviewCardProps {
  projectId: string;
  /** "specialist" or "customer" — picks the right subject phrase in copy. */
  subject: "specialist" | "customer";
}

export function LeaveReviewCard({ projectId, subject }: LeaveReviewCardProps) {
  const { t } = useTranslation();
  const create = useCreateReview(projectId);
  const [rating, setRating] = useState(0);
  const [text, setText] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<{ rating: number; text: string } | null>(null);

  if (submitted) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("review.yourReview")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <StarRating value={submitted.rating} />
          {submitted.text && (
            <p className="text-sm text-muted-foreground whitespace-pre-line">{submitted.text}</p>
          )}
        </CardContent>
      </Card>
    );
  }

  async function onSubmit() {
    setErr(null);
    try {
      const review = await create.mutateAsync({ rating, text: text.trim() || null });
      setSubmitted({ rating: review.rating, text: review.text ?? "" });
    } catch (e: unknown) {
      const message = e instanceof ApiError ? e.localized() : (e as Error).message;
      setErr(message);
    }
  }

  const subjectLabel =
    subject === "specialist"
      ? t("projects.labels.subjectSpecialist")
      : t("projects.labels.subjectCustomer");

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">{t("review.title")}</CardTitle>
        <CardDescription>{t("review.subtitle", { subject: subjectLabel })}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-3">
          <StarRatingInput value={rating} onChange={setRating} />
          <span className="text-sm text-muted-foreground">{rating.toFixed(1)}</span>
        </div>
        <Textarea
          rows={4}
          maxLength={4000}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t("review.placeholder")}
        />
        {err && <p className="text-sm text-destructive">{err}</p>}
        <Button onClick={onSubmit} disabled={create.isPending} className="h-11">
          {create.isPending ? t("review.submitting") : t("review.submit")}
        </Button>
      </CardContent>
    </Card>
  );
}
