/**
 * Stash for an in-progress project the visitor was about to publish before
 * we forced them through the auth wall. Lives in sessionStorage so it's
 * scoped to a single browser tab — we don't want it leaking across sessions
 * or surviving a tab close.
 */

const KEY = "doings.pendingProject";

export interface PendingProjectValues {
  title: string;
  description: string;
  budget: number;
  currency: string;
  deadline?: string | "";
  template_id?: string;
  category?: string;
}

interface PendingProject {
  intent: "publish-project";
  values: PendingProjectValues;
  savedAt: number;
}

export function savePendingProject(values: PendingProjectValues): void {
  if (typeof window === "undefined") return;
  const payload: PendingProject = {
    intent: "publish-project",
    values,
    savedAt: Date.now(),
  };
  try {
    sessionStorage.setItem(KEY, JSON.stringify(payload));
  } catch {
    // sessionStorage can throw in private mode / quota exceeded — drop silently
  }
}

export function loadPendingProject(): PendingProject | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as PendingProject;
    if (parsed.intent !== "publish-project") return null;
    return parsed;
  } catch {
    return null;
  }
}

export function clearPendingProject(): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
}
