import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useMyProfile } from "../api";
import { useMySpecialistProjects } from "@/features/projects/api";

export function SpecialistDashboard() {
  const { data: profile } = useMyProfile();
  const { data: mine } = useMySpecialistProjects();

  return (
    <div className="space-y-6">
      {profile === null && (
        <Card>
          <CardHeader>
            <CardTitle>Finish your profile</CardTitle>
            <CardDescription>You need a profile before you can apply to projects.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link to="/s/profile">Create profile</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Browse projects</CardTitle>
            <CardDescription>Find new opportunities matching your skills.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link to="/s/feed">Open feed</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Active projects</CardTitle>
            <CardDescription>{mine?.items.length ?? 0} engaged</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {mine?.items
                .filter((p) => p.status === "in_progress")
                .slice(0, 3)
                .map((p) => (
                  <li key={p.id}>
                    <Link to={`/s/projects/${p.id}`} className="hover:underline">
                      {p.title}
                    </Link>
                  </li>
                ))}
              {mine && mine.items.length === 0 && (
                <li className="text-muted-foreground">No active projects yet.</li>
              )}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Your rating</CardTitle>
            <CardDescription>Built from customer reviews</CardDescription>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">
            {profile ? `${Number(profile.rating_avg).toFixed(2)} ★` : "—"}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
