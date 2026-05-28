// Predefined avatar gallery. Avatars are an animal emoji rendered on a
// colored background tile. Backend stores only the composite id string
// "animal:color"; the frontend registry is the source of truth for rendering.

export interface AnimalEntry {
  id: string;
  emoji: string;
  label: string;
}

export interface ColorEntry {
  id: string;
  /** Background utility class. */
  bg: string;
  /** Foreground emoji wrapper class — usually unused; emojis carry their own color. */
  ring: string;
  label: string;
}

export const ANIMALS: readonly AnimalEntry[] = [
  { id: "fox", emoji: "🦊", label: "Fox" },
  { id: "owl", emoji: "🦉", label: "Owl" },
  { id: "cat", emoji: "🐱", label: "Cat" },
  { id: "otter", emoji: "🦦", label: "Otter" },
  { id: "panda", emoji: "🐼", label: "Panda" },
  { id: "koala", emoji: "🐨", label: "Koala" },
  { id: "bear", emoji: "🐻", label: "Bear" },
  { id: "wolf", emoji: "🐺", label: "Wolf" },
  { id: "deer", emoji: "🦌", label: "Deer" },
  { id: "frog", emoji: "🐸", label: "Frog" },
  { id: "penguin", emoji: "🐧", label: "Penguin" },
  { id: "turtle", emoji: "🐢", label: "Turtle" },
];

export const COLORS: readonly ColorEntry[] = [
  { id: "amber", bg: "bg-amber-100 dark:bg-amber-900/30", ring: "ring-amber-200", label: "Amber" },
  { id: "rose", bg: "bg-rose-100 dark:bg-rose-900/30", ring: "ring-rose-200", label: "Rose" },
  { id: "emerald", bg: "bg-emerald-100 dark:bg-emerald-900/30", ring: "ring-emerald-200", label: "Emerald" },
  { id: "sky", bg: "bg-sky-100 dark:bg-sky-900/30", ring: "ring-sky-200", label: "Sky" },
  { id: "violet", bg: "bg-violet-100 dark:bg-violet-900/30", ring: "ring-violet-200", label: "Violet" },
  { id: "slate", bg: "bg-slate-200 dark:bg-slate-700/40", ring: "ring-slate-300", label: "Slate" },
  { id: "stone", bg: "bg-stone-200 dark:bg-stone-700/40", ring: "ring-stone-300", label: "Stone" },
  { id: "neutral", bg: "bg-neutral-200 dark:bg-neutral-700/40", ring: "ring-neutral-300", label: "Neutral" },
];

export const DEFAULT_ANIMAL_ID = "fox";
export const DEFAULT_COLOR_ID = "amber";
export const DEFAULT_AVATAR_ID = `${DEFAULT_ANIMAL_ID}:${DEFAULT_COLOR_ID}`;

const ANIMAL_BY_ID = new Map(ANIMALS.map((a) => [a.id, a]));
const COLOR_BY_ID = new Map(COLORS.map((c) => [c.id, c]));

export function parseAvatarId(id: string | null | undefined): {
  animal: AnimalEntry;
  color: ColorEntry;
} {
  const [animalId = DEFAULT_ANIMAL_ID, colorId = DEFAULT_COLOR_ID] = (id ?? "").split(":");
  return {
    animal: ANIMAL_BY_ID.get(animalId) ?? ANIMAL_BY_ID.get(DEFAULT_ANIMAL_ID)!,
    color: COLOR_BY_ID.get(colorId) ?? COLOR_BY_ID.get(DEFAULT_COLOR_ID)!,
  };
}

export function formatAvatarId(animalId: string, colorId: string): string {
  return `${animalId}:${colorId}`;
}
