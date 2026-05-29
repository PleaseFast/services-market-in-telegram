import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { StarRatingInput } from "@/features/specialist/components/reviews/StarRatingInput";
import { StarRating } from "@/features/specialist/components/reviews/StarRating";
import { useCreateReview } from "@/features/projects/api";

interface LeaveReviewCardProps {
  projectId: string;
  /** "the specialist" or "the customer" — used in copy. */
  subjectLabel: string;
}

export function LeaveReviewCard({ projectId, subjectLabel }: LeaveReviewCardProps) {
  const create = useCreateReview(projectId);
  const [rating, setRating] = useState(0);
  const [text, setText] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<{ rating: number; text: string } | null>(null);

  if (submitted) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Your review</CardTitle>
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
      const status = (e as { status?: number }).status;
      if (status === 409) {
        setErr("You've already reviewed this project.");
      } else {
        setErr((e as Error).message);
      }
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">Leave a review</CardTitle>
        <CardDescription>
          Rate {subjectLabel} (0–5 stars, half-star steps) and leave an optional note.
        </CardDescription>
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
          placeholder="What stood out?"
        />
        {err && <p className="text-sm text-destructive">{err}</p>}
        <Button onClick={onSubmit} disabled={create.isPending} className="h-11">
          {create.isPending ? "Submitting…" : "Submit review"}
        </Button>
      </CardContent>
    </Card>
  );
}
