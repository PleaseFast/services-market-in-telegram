import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  Archive,
  Bell,
  Briefcase,
  Compass,
  FolderKanban,
  LayoutDashboard,
  LogOut,
  Moon,
  Plus,
  Sun,
  User,
  Users,
} from "lucide-react";
import { useEffect, useState, type ComponentType, type SVGProps } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/stores/auth";
import { cn } from "@/lib/utils";

type Icon = ComponentType<SVGProps<SVGSVGElement>>;
interface NavItem {
  to: string;
  label: string;
  icon: Icon;
}

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

function buildNav(
  isAuthed: boolean,
  role: "specialist" | "customer" | null,
  isGuest: boolean,
): NavItem[] {
  if (isGuest) {
    return [{ to: "/s/feed", label: "Browse projects", icon: Compass }];
  }
  if (!isAuthed || !role) return [];
  if (role === "specialist") {
    return [
      { to: "/s", label: "Dashboard", icon: LayoutDashboard },
      { to: "/s/feed", label: "Projects", icon: Briefcase },
      { to: "/s/profile", label: "Profile", icon: User },
      { to: "/s/archive", label: "Archive", icon: Archive },
    ];
  }
  return [
    { to: "/c", label: "Dashboard", icon: LayoutDashboard },
    { to: "/c/projects", label: "My projects", icon: FolderKanban },
    { to: "/c/new", label: "New project", icon: Plus },
    { to: "/c/specialists", label: "Specialists", icon: Users },
  ];
}

export function Shell() {
  const { user, isGuest, logout, exitGuest } = useAuthStore();
  const accessToken = useAuthStore((s) => s.accessToken);
  const isAuthed = !!accessToken && !!user;
  const nav = useNavigate();
  const location = useLocation();
  const items = buildNav(isAuthed, user?.role ?? null, isGuest);
  const hasSidebar = items.length > 0;

  // On the landing page we want a maximally clean layout (no sidebar even
  // for authenticated users) so the hero owns the canvas.
  const isLanding = location.pathname === "/";
  const showSidebar = hasSidebar && !isLanding;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-20 border-b bg-background/80 backdrop-blur">
        <div className="container mx-auto flex items-center justify-between px-4 h-14 gap-4">
          <Link to="/" className="font-semibold text-lg flex items-center gap-2 tracking-tight">
            Doings
            {isGuest && <Badge tone="default">Guest</Badge>}
          </Link>

          <div className="flex items-center gap-1">
            {!isAuthed && !isGuest && (
              <div className="hidden sm:flex items-center gap-1 mr-1">
                <Button asChild variant="ghost" size="sm">
                  <Link to="/register?role=customer">For customers</Link>
                </Button>
                <Button asChild variant="ghost" size="sm">
                  <Link to="/register?role=specialist">For specialists</Link>
                </Button>
                <Button asChild variant="outline" size="sm">
                  <Link to="/login">Sign in</Link>
                </Button>
              </div>
            )}
            {isGuest && (
              <Button asChild variant="outline" size="sm" className="mr-1">
                <Link to="/register">Sign up</Link>
              </Button>
            )}
            {isAuthed && (
              <Button variant="ghost" size="icon" asChild aria-label="Notifications">
                <Link to="/notifications">
                  <Bell className="h-4 w-4" />
                </Link>
              </Button>
            )}
            <ThemeToggle />
            {isAuthed && (
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
          <div className="border-t bg-muted/60">
            <div className="container mx-auto px-4 py-2 text-xs flex items-center justify-between gap-4 text-muted-foreground">
              <span>
                Browsing as a guest — applying, chatting, and posting projects need an account.
              </span>
              <span className="flex gap-3 shrink-0">
                <Link to="/register" className="underline underline-offset-4 hover:text-foreground">
                  Create account
                </Link>
                <Link to="/login" className="underline underline-offset-4 hover:text-foreground">
                  Sign in
                </Link>
              </span>
            </div>
          </div>
        )}
      </header>

      <div className="flex-1 flex">
        {showSidebar && (
          <aside className="hidden md:flex md:flex-col w-56 border-r shrink-0 py-6 px-3 gap-1">
            {items.map((item) => (
              <SidebarLink key={item.to} item={item} />
            ))}
          </aside>
        )}
        <main className={cn("flex-1 px-4 py-6 pb-24 md:pb-10", showSidebar ? "md:px-8" : "")}>
          <div className={cn("mx-auto w-full", showSidebar ? "max-w-5xl" : "container")}>
            <Outlet />
          </div>
        </main>
      </div>

      {hasSidebar && (
        <nav
          className="md:hidden fixed bottom-0 inset-x-0 z-20 border-t bg-background/95 backdrop-blur"
          style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
        >
          <ul className="flex">
            {items.map((item) => (
              <li key={item.to} className="flex-1">
                <NavLink
                  to={item.to}
                  end={item.to === "/s" || item.to === "/c"}
                  className={({ isActive }) =>
                    cn(
                      "flex flex-col items-center justify-center gap-0.5 py-2.5 text-[11px]",
                      isActive ? "text-foreground" : "text-muted-foreground",
                    )
                  }
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      )}

      <footer className="hidden md:block border-t py-6 text-center text-xs text-muted-foreground">
        Doings — Telegram-native IT freelance marketplace.
      </footer>
    </div>
  );
}

function SidebarLink({ item }: { item: NavItem }) {
  return (
    <NavLink
      to={item.to}
      end={item.to === "/s" || item.to === "/c"}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
          isActive
            ? "bg-muted text-foreground font-medium"
            : "text-muted-foreground hover:bg-muted hover:text-foreground",
        )
      }
    >
      <item.icon className="h-4 w-4 shrink-0" />
      {item.label}
    </NavLink>
  );
}
