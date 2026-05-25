import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { http } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface NotificationItem {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  read_at: string | null;
  created_at: string;
}

export function NotificationsPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => http.get<NotificationItem[]>("/notifications"),
  });
  const markRead = useMutation({
    mutationFn: (id: string) => http.post(`/notifications/${id}/read`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Notifications</h1>
      <div className="space-y-2">
        {data?.length === 0 && (
          <p className="text-muted-foreground text-sm">Nothing yet — quiet day.</p>
        )}
        {data?.map((n) => (
          <Card key={n.id}>
            <CardHeader>
              <div className="flex justify-between items-center gap-2">
                <CardTitle className="text-base">{prettyType(n.type)}</CardTitle>
                {!n.read_at && <Badge tone="primary">new</Badge>}
              </div>
            </CardHeader>
            <CardContent className="flex justify-between items-center">
              <pre className="text-xs text-muted-foreground whitespace-pre-wrap">
                {JSON.stringify(n.payload, null, 2)}
              </pre>
              {!n.read_at && (
                <Button size="sm" variant="ghost" onClick={() => markRead.mutate(n.id)}>
                  Mark read
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function prettyType(t: string): string {
  return t.replace(/_/g, " ");
}
