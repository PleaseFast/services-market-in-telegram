import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { z } from "zod";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { register as registerApi } from "../api";
import { useAuthStore } from "@/stores/auth";
import { ApiError } from "@/lib/api";

type FormValues = {
  email: string;
  password: string;
  role: "specialist" | "customer";
};

function safeNext(raw: string | null): string | null {
  if (!raw) return null;
  // Only accept same-origin relative paths to avoid open-redirect.
  if (!raw.startsWith("/") || raw.startsWith("//")) return null;
  return raw;
}

export function RegisterPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const [params] = useSearchParams();
  const next = safeNext(params.get("next"));
  const lockedRole = params.get("role");
  const isRoleLocked = lockedRole === "customer" || lockedRole === "specialist";
  const enterGuest = useAuthStore((s) => s.enterGuest);

  const [err, setErr] = useState<string | null>(null);

  const schema = useMemo(
    () =>
      z.object({
        email: z.string().email(t("validation.email")),
        password: z.string().min(8, t("validation.passwordMin", { count: 8 })),
        role: z.enum(["specialist", "customer"]),
      }),
    [t],
  );

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
      const message = e instanceof ApiError ? e.localized() : (e as Error).message;
      setErr(message);
    }
  }

  const signInHref = `/login${params.toString() ? `?${params.toString()}` : ""}`;

  return (
    <div className="max-w-md mx-auto pt-12">
      <Card className="border-0 shadow-none md:border md:shadow-sm">
        <CardHeader>
          <CardTitle className="text-2xl">{t("auth.register.title")}</CardTitle>
          {isRoleLocked && lockedRole === "customer" && (
            <p className="text-sm text-muted-foreground">{t("auth.register.intentCustomer")}</p>
          )}
          {isRoleLocked && lockedRole === "specialist" && (
            <p className="text-sm text-muted-foreground">{t("auth.register.intentSpecialist")}</p>
          )}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {!isRoleLocked && (
              <div className="space-y-1.5">
                <Label>{t("auth.register.roleLabel")}</Label>
                <div className="grid grid-cols-2 gap-2">
                  {(["customer", "specialist"] as const).map((r) => (
                    <Button
                      type="button"
                      key={r}
                      variant={role === r ? "default" : "outline"}
                      onClick={() => setValue("role", r)}
                    >
                      {r === "customer"
                        ? t("auth.register.roleCustomer")
                        : t("auth.register.roleSpecialist")}
                    </Button>
                  ))}
                </div>
                <input type="hidden" {...register("role")} />
              </div>
            )}
            <div className="space-y-1.5">
              <Label htmlFor="email">{t("auth.register.emailLabel")}</Label>
              <Input id="email" type="email" {...register("email")} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">{t("auth.register.passwordLabel")}</Label>
              <Input id="password" type="password" {...register("password")} />
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>
            {err && <p className="text-sm text-destructive">{err}</p>}
            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? t("auth.register.submitting") : t("auth.register.submit")}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              {t("auth.register.haveAccount")}{" "}
              <Link to={signInHref} className="text-foreground underline-offset-4 hover:underline">
                {t("auth.register.signIn")}
              </Link>
            </p>
          </form>
          {showGuestOption && (
            <div className="mt-6 pt-5 border-t text-center space-y-1">
              <p className="text-sm text-muted-foreground">{t("auth.register.notReady")}</p>
              <button
                type="button"
                onClick={() => {
                  enterGuest();
                  nav("/s/feed");
                }}
                className="text-sm font-medium text-foreground underline underline-offset-4 hover:opacity-80"
              >
                {t("auth.register.browseAsGuest")}
              </button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
