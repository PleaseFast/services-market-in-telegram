import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth";

export function LandingPage() {
  const { user, enterGuest } = useAuthStore();
  const nav = useNavigate();
  return (
    <div className="space-y-12 py-8">
      <section className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
          IT freelance — <span className="text-primary">native to Telegram</span>
        </h1>
        <p className="text-muted-foreground max-w-xl mx-auto">
          Post projects, find specialists, and chat anonymously — without ever
          leaving the app you already use.
        </p>
        <div className="flex gap-2 justify-center">
          {user ? (
            <Button asChild>
              <Link to={user.role === "customer" ? "/c" : "/s"}>Open dashboard</Link>
            </Button>
          ) : (
            <>
              <Button asChild>
                <Link to="/register">Get started</Link>
              </Button>
              <Button asChild variant="outline">
                <Link to="/login">Sign in</Link>
              </Button>
              <Button
                variant="ghost"
                onClick={() => {
                  enterGuest();
                  nav("/s/feed");
                }}
              >
                Continue as guest
              </Button>
            </>
          )}
        </div>
        {!user && (
          <p className="text-xs text-muted-foreground">
            Guests can browse open projects. Applying, chatting, and posting projects require an account.
          </p>
        )}
      </section>

      <section className="grid md:grid-cols-3 gap-4">
        {[
          {
            title: "For customers",
            body: "Pick from popular IT request templates, describe your scope, and start receiving applicants the same day.",
          },
          {
            title: "For specialists",
            body: "Browse open projects, apply with a cover letter, and chat anonymously via RefereeBot until a deal is struck.",
          },
          {
            title: "Telegram-first",
            body: "DoersBot and CustomersBot handle notifications. RefereeBot relays first-contact conversations anonymously.",
          },
        ].map((c) => (
          <Card key={c.title}>
            <CardHeader>
              <CardTitle>{c.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{c.body}</p>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
