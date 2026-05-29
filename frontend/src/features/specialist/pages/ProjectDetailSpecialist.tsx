import { useParams } from "react-router-dom";
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useApply, useProject } from "@/features/projects/api";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import { GuestPrompt } from "@/components/GuestPrompt";

export function ProjectDetailSpecialist() {
  const { id } = useParams<{ id: string }>();
  const { data: project, isLoading } = useProject(id);
  const apply = useApply();
  const [cover, setCover] = useState("");
  const [done, setDone] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const isGuest = useAuthStore((s) => s.isGuest);

  if (isLoading) return <p className="text-muted-foreground text-sm">Loading…</p>;
  if (!project) return <p>Project not found.</p>;

  const publishedDisplay = formatDate(project.published_at ?? project.created_at);
  const higher = project.higher_rated_applicants ?? 0;

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start gap-2">
            <div>
              <CardTitle className="text-xl font-semibold tracking-tight">
                {project.title}
              </CardTitle>
              <CardDescription>
                Budget: {project.budget} {project.currency} · Deadline: {formatDate(project.deadline)}
              </CardDescription>
              <p className="text-xs text-muted-foreground mt-1">
                Published: {publishedDisplay}
              </p>
            </div>
            <Badge tone="outline">{project.status}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {higher > 0 && (
            <p className="text-xs rounded-md border border-amber-500/40 bg-amber-50 text-amber-800 px-3 py-2">
              {higher === 1
                ? "1 applicant has a higher rating than you"
                : `${higher} applicants have a higher rating than you`}
            </p>
          )}
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{project.description}</p>
        </CardContent>
      </Card>

      {isGuest && project.status === "open" && (
        <GuestPrompt action="apply to this project" />
      )}

      {!isGuest && project.status === "open" && !done && (
        <Card>
          <CardHeader>
            <CardTitle>Apply</CardTitle>
            <CardDescription>Add a short cover letter (optional).</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              rows={5}
              value={cover}
              onChange={(e) => setCover(e.target.value)}
              placeholder="Hi! Here's why I'm a good fit…"
            />
            {err && <p className="text-sm text-destructive">{err}</p>}
            <Button
              disabled={apply.isPending}
              onClick={async () => {
                setErr(null);
                try {
                  await apply.mutateAsync({ projectId: project.id, coverLetter: cover || undefined });
                  setDone(true);
                } catch (e: unknown) {
                  setErr((e as Error).message);
                }
              }}
            >
              {apply.isPending ? "Sending…" : "Send application"}
            </Button>
          </CardContent>
        </Card>
      )}

      {done && (
        <Card>
          <CardContent className="pt-6">
            ✅ Application sent. Customer will be notified.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
