import { useParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  useApplicants,
  useArchiveProject,
  useCompleteProject,
  useProject,
  usePublishProject,
  useSelectSpecialist,
} from "@/features/projects/api";
import { formatDate } from "@/lib/utils";

export function CustomerProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: project } = useProject(id);
  const { data: applicants } = useApplicants(
    project && project.status !== "draft" ? id : undefined,
  );
  const publish = usePublishProject();
  const select = useSelectSpecialist();
  const complete = useCompleteProject();
  const archive = useArchiveProject();

  if (!project) return <p className="text-muted-foreground text-sm">Loading…</p>;

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
            </div>
            <Badge tone="outline">{project.status}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{project.description}</p>
          <div className="flex flex-wrap gap-2">
            {project.status === "draft" && (
              <Button onClick={() => publish.mutate(project.id)} disabled={publish.isPending}>
                Publish
              </Button>
            )}
            {project.status === "in_progress" && (
              <Button onClick={() => complete.mutate(project.id)} disabled={complete.isPending}>
                Mark complete
              </Button>
            )}
            {["completed", "canceled"].includes(project.status) && (
              <Button variant="outline" onClick={() => archive.mutate(project.id)} disabled={archive.isPending}>
                Archive
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {project.status === "open" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium">Applicants ({applicants?.length ?? 0})</CardTitle>
            <CardDescription>
              Open RefereeBot in Telegram to chat anonymously, then come back here to select.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y">
              {applicants?.map((a, idx) => (
                <li key={a.id} className="py-3 flex justify-between items-start gap-4">
                  <div>
                    <p className="font-medium">Anonymous specialist #{idx + 1}</p>
                    {a.cover_letter && (
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap mt-1">
                        {a.cover_letter}
                      </p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    onClick={() =>
                      select.mutate({ projectId: project.id, specialistId: a.specialist_id })
                    }
                    disabled={select.isPending}
                  >
                    Select
                  </Button>
                </li>
              ))}
              {applicants && applicants.length === 0 && (
                <li className="py-3 text-sm text-muted-foreground">No applicants yet.</li>
              )}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
