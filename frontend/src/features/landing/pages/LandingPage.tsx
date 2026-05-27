import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, BadgeCheck, MessageSquareText, Sparkles, Wallet } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/auth";
import { useTemplates, usePublicFeed } from "@/features/projects/api";
import { groupByCategory } from "@/lib/templates";
import { cn } from "@/lib/utils";

const FEATURES = [
  {
    icon: MessageSquareText,
    title: "Specialists scope the job",
    body: "Tell us about your project. Pros read it and respond with proposals.",
  },
  {
    icon: Wallet,
    title: "Best price",
    body: "Compare quotes from multiple specialists and pick the one that fits.",
  },
  {
    icon: BadgeCheck,
    title: "Verified pros",
    body: "We check identity, experience, and the work history of every specialist.",
  },
  {
    icon: Sparkles,
    title: "Real reviews",
    body: "Reviews can only be left after the job is finished — no astroturf.",
  },
];

const LANDING_VISIBLE_PER_CATEGORY = 6;

export function LandingPage() {
  const nav = useNavigate();
  const { user, isGuest, enterGuest } = useAuthStore();
  const { data: templates } = useTemplates();
  const { data: feed } = usePublicFeed();
  const [q, setQ] = useState("");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const grouped = useMemo(() => groupByCategory(templates ?? []), [templates]);
  const openProjectCount = feed?.total ?? 0;

  function submitSearch() {
    const trimmed = q.trim();
    nav(trimmed ? `/s/feed?q=${encodeURIComponent(trimmed)}` : "/s/feed");
  }

  return (
    <div className="space-y-20 pb-12">
      {/* HERO */}
      <section className="pt-12 md:pt-16 max-w-3xl">
        <h1 className="text-4xl md:text-6xl font-semibold tracking-tight leading-[1.05]">
          Quick search for IT specialists
        </h1>
        <p className="mt-4 text-muted-foreground text-base md:text-lg">
          {openProjectCount > 0
            ? `${openProjectCount.toLocaleString()} open projects — find the right specialist or post your own.`
            : "Find the right specialist or post your own project."}
        </p>

        <div className="mt-8 flex flex-col sm:flex-row gap-2 max-w-2xl">
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") submitSearch();
            }}
            placeholder="Service or specialist…"
            className="h-12 text-base rounded-xl bg-muted/60 border-transparent focus-visible:bg-background"
          />
          <Button onClick={submitSearch} className="h-12 px-6 rounded-xl">
            Find
            <ArrowRight className="ml-1 h-4 w-4" />
          </Button>
        </div>

        <div className="mt-6 flex flex-wrap gap-3 items-center text-sm">
          {user ? (
            <Button asChild variant="outline">
              <Link to={user.role === "customer" ? "/c" : "/s"}>Open dashboard</Link>
            </Button>
          ) : (
            <>
              <Button asChild>
                <Link to="/c/new">Post a project</Link>
              </Button>
              {!isGuest && (
                <Button
                  variant="ghost"
                  onClick={() => {
                    enterGuest();
                    nav("/s/feed");
                  }}
                >
                  Continue as guest
                </Button>
              )}
              <Link to="/register?role=specialist" className="text-muted-foreground hover:text-foreground underline-offset-4 hover:underline">
                I&apos;m a specialist
              </Link>
            </>
          )}
        </div>
      </section>

      {/* FEATURES */}
      <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-10">
        {FEATURES.map((f) => (
          <div key={f.title} className="space-y-3">
            <div className="h-10 w-10 flex items-center justify-center rounded-full bg-muted">
              <f.icon className="h-5 w-5" />
            </div>
            <h3 className="font-medium">{f.title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{f.body}</p>
          </div>
        ))}
      </section>

      {/* STATS */}
      <section className="text-sm text-muted-foreground">
        {openProjectCount > 0
          ? `${openProjectCount.toLocaleString()} projects open right now, with new ones posted daily.`
          : "Be the first — post a project today."}
      </section>

      {/* CATEGORY GRID */}
      {grouped.length > 0 && (
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-10 gap-y-10">
          {grouped.map(({ category, items }) => {
            const isExpanded = expanded[category] ?? false;
            const visible = isExpanded ? items : items.slice(0, LANDING_VISIBLE_PER_CATEGORY);
            const hidden = items.length - visible.length;
            return (
              <div key={category} className="space-y-3">
                <div className="flex items-baseline gap-2">
                  <h3 className="font-semibold">{category}</h3>
                  <span className="text-xs text-muted-foreground">{items.length}</span>
                </div>
                <ul className="space-y-1.5">
                  {visible.map((t) => (
                    <li key={t.id}>
                      <Link
                        to={`/c/new?template_id=${t.id}`}
                        className={cn(
                          "text-sm text-muted-foreground hover:text-foreground",
                          "hover:underline underline-offset-4",
                        )}
                      >
                        {t.title}
                      </Link>
                    </li>
                  ))}
                </ul>
                {items.length > LANDING_VISIBLE_PER_CATEGORY && (
                  <button
                    type="button"
                    onClick={() => setExpanded((s) => ({ ...s, [category]: !isExpanded }))}
                    className="text-xs text-muted-foreground hover:text-foreground underline-offset-4 hover:underline"
                  >
                    {isExpanded ? "Show less" : `Show ${hidden} more`}
                  </button>
                )}
              </div>
            );
          })}
        </section>
      )}
    </div>
  );
}
