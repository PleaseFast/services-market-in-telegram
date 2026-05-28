import { cn } from "@/lib/utils";
import { parseAvatarId } from "@/lib/avatars";

type AvatarSize = "sm" | "md" | "lg" | "xl";

const SIZES: Record<AvatarSize, { box: string; emoji: string }> = {
  sm: { box: "h-8 w-8 rounded-md text-base", emoji: "text-lg" },
  md: { box: "h-12 w-12 rounded-lg text-xl", emoji: "text-2xl" },
  lg: { box: "h-24 w-24 rounded-xl text-4xl", emoji: "text-5xl" },
  xl: { box: "h-40 w-40 rounded-2xl text-6xl", emoji: "text-7xl" },
};

export function Avatar({
  avatarId,
  size = "md",
  className,
  title,
}: {
  avatarId: string | null | undefined;
  size?: AvatarSize;
  className?: string;
  title?: string;
}) {
  const { animal, color } = parseAvatarId(avatarId);
  const s = SIZES[size];
  return (
    <div
      role="img"
      aria-label={title ?? `${animal.label} ${color.label}`}
      title={title ?? `${animal.label} ${color.label}`}
      className={cn(
        "inline-flex shrink-0 items-center justify-center select-none",
        color.bg,
        s.box,
        className,
      )}
    >
      <span className={cn("leading-none", s.emoji)} aria-hidden>
        {animal.emoji}
      </span>
    </div>
  );
}
