import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { register as registerApi } from "../api";
import { useAuthStore } from "@/stores/auth";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8, "Min 8 characters"),
  role: z.enum(["specialist", "customer"]),
});

type FormValues = z.infer<typeof schema>;

function safeNext(raw: string | null): string | null {
  if (!raw) return null;
  // Only accept same-origin relative paths to avoid open-redirect.
  if (!raw.startsWith("/") || raw.startsWith("//")) return null;
  return raw;
}

export function RegisterPage() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const next = safeNext(params.get("next"));
  const lockedRole = params.get("role");
  const isRoleLocked = lockedRole === "customer" || lockedRole === "specialist";
  const enterGuest = useAuthStore((s) => s.enterGuest);

  const [err, setErr] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { role: isRoleLocked ? (lockedRole as "customer" | "specialist") : "customer" },
  });
  const role = watch("role");
  // The guest path is offered only inside the specialist auth flow — either
  // the role is locked to specialist (came from the "For specialists" header
  // entry point) or the user has actively picked "Specialist" in the role
  // selector. Customers don't browse anonymously here.
  const showGuestOption = isRoleLocked
    ? lockedRole === "specialist"
    : role === "specialist";

  useEffect(() => {
    if (isRoleLocked) setValue("role", lockedRole as "customer" | "specialist");
  }, [isRoleLocked, lockedRole, setValue]);

  async function onSubmit(values: FormValues) {
    setErr(null);
    try {
      const me = await registerApi(
        values.email,
        values.password,
        isRoleLocked ? (lockedRole as "customer" | "specialist") : values.role,
      );
      if (next) {
        // Forward search params (autosubmit, etc.) onto the destination.
        const fwd = new URLSearchParams();
        for (const [k, v] of params.entries()) {
          if (k !== "next" && k !== "role") fwd.set(k, v);
        }
        const sep = next.includes("?") ? "&" : "?";
        nav(fwd.toString() ? `${next}${sep}${fwd.toString()}` : next);
        return;
      }
      nav(me.role === "customer" ? "/c/profile?onboarding=1" : "/s/profile?onboarding=1");
    } catch (e: unknown) {
      setErr((e as Error).message);
    }
  }

  // Preserve search params on the "Sign in" link so the auth context isn't lost.
  const signInHref = `/login${params.toString() ? `?${params.toString()}` : ""}`;

  return (
    <div className="max-w-md mx-auto pt-12">
      <Card className="border-0 shadow-none md:border md:shadow-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Create your account</CardTitle>
          {isRoleLocked && lockedRole === "customer" && (
            <p className="text-sm text-muted-foreground">
              You're publishing a project — we&apos;ll create a customer account so you can manage it.
            </p>
          )}
          {isRoleLocked && lockedRole === "specialist" && (
            <p className="text-sm text-muted-foreground">
              Set up your specialist account to apply to projects.
            </p>
          )}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {!isRoleLocked && (
              <div className="space-y-1.5">
                <Label>I am a…</Label>
                <div className="grid grid-cols-2 gap-2">
                  {(["customer", "specialist"] as const).map((r) => (
                    <Button
                      type="button"
                      key={r}
                      variant={role === r ? "default" : "outline"}
                      onClick={() => setValue("role", r)}
                    >
                      {r === "customer" ? "Customer" : "Specialist"}
                    </Button>
                  ))}
                </div>
                <input type="hidden" {...register("role")} />
              </div>
            )}
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register("email")} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" {...register("password")} />
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>
            {err && <p className="text-sm text-destructive">{err}</p>}
            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? "Creating…" : "Create account"}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              Already have one?{" "}
              <Link to={signInHref} className="text-foreground underline-offset-4 hover:underline">
                Sign in
              </Link>
            </p>
          </form>
          {showGuestOption && (
            <div className="mt-6 pt-5 border-t text-center space-y-1">
              <p className="text-sm text-muted-foreground">
                Not ready to sign up?
              </p>
              <button
                type="button"
                onClick={() => {
                  enterGuest();
                  nav("/s/feed");
                }}
                className="text-sm font-medium text-foreground underline underline-offset-4 hover:opacity-80"
              >
                Browse projects as a guest
              </button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
