import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { Bell, LogOut, Moon, Sun, UserPlus } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/stores/auth";
import { cn } from "@/lib/utils";

function ThemeToggle() {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains("dark"));
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);
  return (
    <Button variant="ghost" size="icon" onClick={() => setDark((d) => !d)} aria-label="Toggle theme">
      {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </Button>
  );
}

export function Shell() {
  const { user, isGuest, logout, exitGuest } = useAuthStore();
  const nav = useNavigate();

  const links = isGuest
    ? [{ to: "/s/feed", label: "Browse projects" }]
    : !user
      ? [{ to: "/login", label: "Sign in" }]
      : user.role === "specialist"
        ? [
            { to: "/s", label: "Dashboard" },
            { to: "/s/feed", label: "Projects" },
            { to: "/s/profile", label: "Profile" },
            { to: "/s/archive", label: "Archive" },
          ]
        : [
            { to: "/c", label: "Dashboard" },
            { to: "/c/projects", label: "My projects" },
            { to: "/c/new", label: "+ New project" },
            { to: "/c/specialists", label: "Specialists" },
          ];

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
        <div className="container mx-auto flex items-center justify-between px-4 h-14 gap-4">
          <Link to="/" className="font-semibold text-lg flex items-center gap-2">
            Doings
            {isGuest && <Badge tone="warning">Guest</Badge>}
          </Link>
          <nav className="hidden md:flex items-center gap-1">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  cn(
                    "px-3 py-1.5 rounded-md text-sm hover:bg-muted",
                    isActive && "bg-muted font-medium",
                  )
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-1">
            {user && (
              <Button variant="ghost" size="icon" asChild aria-label="Notifications">
                <Link to="/notifications">
                  <Bell className="h-4 w-4" />
                </Link>
              </Button>
            )}
            {isGuest && (
              <Button variant="outline" size="sm" asChild>
                <Link to="/register">
                  <UserPlus className="h-4 w-4 mr-1" />
                  Sign up
                </Link>
              </Button>
            )}
            <ThemeToggle />
            {user && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  logout();
                  nav("/");
                }}
                aria-label="Sign out"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            )}
            {isGuest && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  exitGuest();
                  nav("/");
                }}
                aria-label="Exit guest mode"
                title="Exit guest mode"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
        {isGuest && (
          <div className="border-t bg-amber-500/10 text-amber-900 dark:text-amber-200">
            <div className="container mx-auto px-4 py-2 text-xs flex items-center justify-between gap-4">
              <span>
                You&apos;re browsing as a guest — applying, chatting, and posting projects are
                disabled.
              </span>
              <span className="flex gap-2 shrink-0">
                <Link to="/register" className="underline underline-offset-4">
                  Create account
                </Link>
                <Link to="/login" className="underline underline-offset-4">
                  Sign in
                </Link>
              </span>
            </div>
          </div>
        )}
      </header>
      <main className="flex-1 container mx-auto px-4 py-6">
        <Outlet />
      </main>
      <footer className="border-t py-4 text-center text-xs text-muted-foreground">
        Doings MVP — Telegram-native IT freelance marketplace.
      </footer>
    </div>
  );
}
