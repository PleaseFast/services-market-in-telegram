import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login } from "../api";
import { useAuthStore } from "@/stores/auth";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormValues = z.infer<typeof schema>;

function safeNext(raw: string | null): string | null {
  if (!raw) return null;
  if (!raw.startsWith("/") || raw.startsWith("//")) return null;
  return raw;
}

export function LoginPage() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const next = safeNext(params.get("next"));
  // The guest path surfaces only when the visitor is in the specialist auth
  // flow — they arrived here from "For specialists" (or the register page's
  // sign-in link, which preserves the role param).
  const showGuestOption = params.get("role") === "specialist";
  const enterGuest = useAuthStore((s) => s.enterGuest);
  const [err, setErr] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setErr(null);
    try {
      const me = await login(values.email, values.password);
      if (next) {
        const fwd = new URLSearchParams();
        for (const [k, v] of params.entries()) {
          if (k !== "next" && k !== "role") fwd.set(k, v);
        }
        const sep = next.includes("?") ? "&" : "?";
        nav(fwd.toString() ? `${next}${sep}${fwd.toString()}` : next);
        return;
      }
      nav(me.role === "customer" ? "/c" : "/s");
    } catch (e: unknown) {
      setErr((e as Error).message);
    }
  }

  const signUpHref = `/register${params.toString() ? `?${params.toString()}` : ""}`;

  return (
    <div className="max-w-md mx-auto pt-12">
      <Card className="border-0 shadow-none md:border md:shadow-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Sign in</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
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
              {isSubmitting ? "Signing in…" : "Sign in"}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              No account?{" "}
              <Link to={signUpHref} className="text-foreground underline-offset-4 hover:underline">
                Create one
              </Link>
            </p>
          </form>
          {showGuestOption && (
            <div className="mt-6 pt-5 border-t text-center space-y-1">
              <p className="text-sm text-muted-foreground">
                Not ready to sign in?
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
