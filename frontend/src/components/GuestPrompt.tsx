import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface GuestPromptProps {
  action?: string;
}

export function GuestPrompt({ action = "perform this action" }: GuestPromptProps) {
  return (
    <Card className="border-primary/40">
      <CardHeader>
        <CardTitle>Sign in to continue</CardTitle>
        <CardDescription>
          You need an account to {action}. Guests can only browse open projects.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-2">
        <Button asChild>
          <Link to="/register">Create account</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/login">Sign in</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
