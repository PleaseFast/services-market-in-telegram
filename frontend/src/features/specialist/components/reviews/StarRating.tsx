import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface StarRatingProps {
  value: number; // 0..5
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZES = {
  sm: "h-3.5 w-3.5",
  md: "h-4 w-4",
  lg: "h-5 w-5",
};

/**
 * Read-only stars with a half-step rendering by clipping the filled overlay.
 * 4.6 renders as four solid stars and 60% of the fifth.
 */
export function StarRating({ value, size = "md", className }: StarRatingProps) {
  const clamped = Math.max(0, Math.min(5, value || 0));
  const klass = SIZES[size];
  return (
    <div className={cn("relative inline-flex items-center", className)} aria-label={`${clamped.toFixed(1)} out of 5`}>
      <div className="flex">
        {[0, 1, 2, 3, 4].map((i) => (
          <Star key={`outline-${i}`} className={cn(klass, "text-muted-foreground/40")} />
        ))}
      </div>
      <div
        className="absolute inset-0 flex overflow-hidden"
        style={{ width: `${(clamped / 5) * 100}%` }}
        aria-hidden
      >
        {[0, 1, 2, 3, 4].map((i) => (
          <Star key={`fill-${i}`} className={cn(klass, "text-foreground fill-foreground")} />
        ))}
      </div>
    </div>
  );
}
