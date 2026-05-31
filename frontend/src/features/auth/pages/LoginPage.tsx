import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { z } from "zod";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login } from "../api";
import { useAuthStore } from "@/stores/auth";
import { ApiError } from "@/lib/api";

type FormValues = { email: string; password: string };

function safeNext(raw: string | null): string | null {
  if (!raw) return null;
  if (!raw.startsWith("/") || raw.startsWith("//")) return null;
  return raw;
}

export function LoginPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const [params] = useSearchParams();
  const next = safeNext(params.get("next"));
  const showGuestOption = params.get("role") === "specialist";
  const enterGuest = useAuthStore((s) => s.enterGuest);
  const [err, setErr] = useState<string | null>(null);

  const schema = useMemo(
    () =>
      z.object({
        email: z.string().email(t("validation.email")),
        password: z.string().min(8, t("validation.passwordMin", { count: 8 })),
      }),
    [t],
  );

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
      const message = e instanceof ApiError ? e.localized() : (e as Error).message;
      setErr(message);
    }
  }

  const signUpHref = `/register${params.toString() ? `?${params.toString()}` : ""}`;

  return (
    <div className="max-w-md mx-auto pt-12">
      <Card className="border-0 shadow-none md:border md:shadow-sm">
        <CardHeader>
          <CardTitle className="text-2xl">{t("auth.login.title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="email">{t("auth.login.emailLabel")}</Label>
              <Input id="email" type="email" {...register("email")} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">{t("auth.login.passwordLabel")}</Label>
              <Input id="password" type="password" {...register("password")} />
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>
            {err && <p className="text-sm text-destructive">{err}</p>}
            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? t("auth.login.submitting") : t("auth.login.submit")}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              {t("auth.login.noAccount")}{" "}
              <Link to={signUpHref} className="text-foreground underline-offset-4 hover:underline">
                {t("auth.login.createOne")}
              </Link>
            </p>
          </form>
          {showGuestOption && (
            <div className="mt-6 pt-5 border-t text-center space-y-1">
              <p className="text-sm text-muted-foreground">{t("auth.login.notReady")}</p>
              <button
                type="button"
                onClick={() => {
                  enterGuest();
                  nav("/s/feed");
                }}
                className="text-sm font-medium text-foreground underline underline-offset-4 hover:opacity-80"
              >
                {t("auth.login.browseAsGuest")}
              </button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
