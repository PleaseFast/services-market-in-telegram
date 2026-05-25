import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { Bell, LogOut, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
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
  const { user, logout } = useAuthStore();
  const nav = useNavigate();

  const links = !user
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
          <Link to="/" className="font-semibold text-lg">
            Doings
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
          </div>
        </div>
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
