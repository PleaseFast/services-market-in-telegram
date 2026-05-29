import { useState } from "react";
import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface StarRatingInputProps {
  value: number; // 0..5 step 0.5
  onChange: (value: number) => void;
  disabled?: boolean;
  className?: string;
}

const SIZE = "h-7 w-7";

/**
 * Half-step star input. Each star has two hit zones: clicking the left
 * half sets ``index + 0.5``, the right half sets ``index + 1``. Clicking
 * the current value clears back to 0 so the user can recover from a slip.
 */
export function StarRatingInput({
  value,
  onChange,
  disabled = false,
  className,
}: StarRatingInputProps) {
  const [hover, setHover] = useState<number | null>(null);
  const display = Math.max(0, Math.min(5, hover ?? value));

  function pick(next: number) {
    if (disabled) return;
    const v = Math.max(0, Math.min(5, next));
    // Clicking the current rating clears it; otherwise apply.
    onChange(Math.abs(v - value) < 1e-9 ? 0 : v);
  }

  return (
    <div
      className={cn("relative inline-flex items-center select-none", className)}
      onMouseLeave={() => setHover(null)}
      aria-label={`Rating ${value} out of 5`}
    >
      <div className="flex">
        {[0, 1, 2, 3, 4].map((i) => (
          <Star key={`o-${i}`} className={cn(SIZE, "text-muted-foreground/40")} />
        ))}
      </div>
      <div
        className="absolute inset-0 flex overflow-hidden pointer-events-none"
        style={{ width: `${(display / 5) * 100}%` }}
        aria-hidden
      >
        {[0, 1, 2, 3, 4].map((i) => (
          <Star key={`f-${i}`} className={cn(SIZE, "text-amber-500 fill-amber-500")} />
        ))}
      </div>
      {/* Click/hover hit zones overlaid on top so they win over the fills. */}
      <div className="absolute inset-0 flex">
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={`hit-${i}`} className="relative" style={{ width: "20%" }}>
            <button
              type="button"
              disabled={disabled}
              onMouseEnter={() => setHover(i + 0.5)}
              onClick={() => pick(i + 0.5)}
              className="absolute inset-y-0 left-0 w-1/2 cursor-pointer disabled:cursor-default"
              aria-label={`${i + 0.5} stars`}
            />
            <button
              type="button"
              disabled={disabled}
              onMouseEnter={() => setHover(i + 1)}
              onClick={() => pick(i + 1)}
              className="absolute inset-y-0 right-0 w-1/2 cursor-pointer disabled:cursor-default"
              aria-label={`${i + 1} stars`}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
