import { cn } from "@/lib/utils";
import {
  ANIMALS,
  COLORS,
  DEFAULT_ANIMAL_ID,
  DEFAULT_COLOR_ID,
  formatAvatarId,
  parseAvatarId,
} from "@/lib/avatars";
import { Avatar } from "./Avatar";

interface AvatarPickerProps {
  value: string | null | undefined;
  onChange: (next: string) => void;
}

/**
 * Inline gallery picker — two grids (animals, then colors). The currently
 * selected avatar is previewed at `lg` above the grids. No modal: the picker
 * lives inline on the profile edit page.
 */
export function AvatarPicker({ value, onChange }: AvatarPickerProps) {
  const { animal, color } = parseAvatarId(value);
  const animalId = animal.id ?? DEFAULT_ANIMAL_ID;
  const colorId = color.id ?? DEFAULT_COLOR_ID;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Avatar avatarId={formatAvatarId(animalId, colorId)} size="lg" />
        <div className="text-sm text-muted-foreground">
          <p className="font-medium text-foreground">Choose your avatar</p>
          <p>Pick any animal and any color — your avatar will appear on your profile.</p>
        </div>
      </div>

      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
          Animal
        </p>
        <div className="grid grid-cols-6 sm:grid-cols-12 gap-2">
          {ANIMALS.map((a) => {
            const selected = a.id === animalId;
            return (
              <button
                key={a.id}
                type="button"
                onClick={() => onChange(formatAvatarId(a.id, colorId))}
                className={cn(
                  "h-11 w-11 min-w-[44px] inline-flex items-center justify-center rounded-lg border text-2xl transition-colors",
                  selected
                    ? "border-foreground bg-muted"
                    : "border-border hover:bg-muted",
                )}
                aria-pressed={selected}
                aria-label={a.label}
                title={a.label}
              >
                <span aria-hidden>{a.emoji}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
          Background
        </p>
        <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
          {COLORS.map((c) => {
            const selected = c.id === colorId;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => onChange(formatAvatarId(animalId, c.id))}
                className={cn(
                  "h-11 w-11 min-w-[44px] inline-flex items-center justify-center rounded-lg border transition-colors",
                  c.bg,
                  selected ? "border-foreground" : "border-transparent",
                )}
                aria-pressed={selected}
                aria-label={c.label}
                title={c.label}
              >
                <span className="sr-only">{c.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
