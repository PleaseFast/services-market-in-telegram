import { Link, useParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/avatar/Avatar";
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
              Tap a specialist to view their full profile, or pick one to start the project.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y">
              {applicants?.map((a) => (
                <li
                  key={a.id}
                  className="py-3 flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3"
                >
                  <Link
                    to={`/specialists/${a.specialist_id}`}
                    className="flex items-start gap-3 flex-1 min-w-0 group"
                  >
                    <Avatar avatarId={a.specialist?.avatar_id} size="md" />
                    <div className="min-w-0">
                      <p className="font-medium group-hover:underline underline-offset-2">
                        {a.specialist?.full_name ?? "Specialist"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {a.specialist?.category ?? "—"} ·{" "}
                        {a.specialist
                          ? `${a.specialist.rating_avg.toFixed(2)} ★ (${a.specialist.rating_count})`
                          : "no rating yet"}
                      </p>
                      {a.cover_letter && (
                        <p className="text-sm text-muted-foreground whitespace-pre-wrap mt-1">
                          {a.cover_letter}
                        </p>
                      )}
                    </div>
                  </Link>
                  <Button
                    size="sm"
                    className="h-11 sm:h-9 self-start"
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
