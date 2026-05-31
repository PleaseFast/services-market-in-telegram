import i18n from "@/i18n";

/** Localized label for a `ProjectStatus` enum value. Falls back to the raw
 * status string if no translation is wired up yet (defensive — should not
 * happen for the closed enum). */
export function projectStatusLabel(status: string): string {
  const key = `projects.status.${status}`;
  const translated = i18n.t(key);
  return typeof translated === "string" && translated !== key ? translated : status;
}
