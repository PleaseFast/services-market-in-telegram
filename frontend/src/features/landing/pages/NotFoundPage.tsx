import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <div className="py-24 text-center space-y-5">
      <h1 className="text-5xl font-semibold tracking-tight">404</h1>
      <p className="text-muted-foreground">This page wandered off.</p>
      <Button asChild>
        <Link to="/">Take me home</Link>
      </Button>
    </div>
  );
}
