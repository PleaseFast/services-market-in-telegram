import { useEffect, useMemo, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { AvatarPicker } from "@/components/avatar/AvatarPicker";
import { DEFAULT_AVATAR_ID } from "@/lib/avatars";
import { useAuthStore } from "@/stores/auth";
import { useMyCustomerProfile, useSaveCustomerProfile } from "../api";

type FormValues = { display_name: string; avatar_id: string };

export function CustomerProfilePage() {
  const { t } = useTranslation();
  const { data: profile } = useMyCustomerProfile();
  const save = useSaveCustomerProfile();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const isOnboarding = params.get("onboarding") === "1";
  const setProfileComplete = useAuthStore((s) => s.setProfileComplete);
  const [ok, setOk] = useState(false);

  const schema = useMemo(
    () =>
      z.object({
        display_name: z
          .string()
          .min(2, t("customer.profile.displayNameMin", { count: 2 }))
          .max(120, t("customer.profile.displayNameMax")),
        avatar_id: z.string().min(1).max(40),
      }),
    [t],
  );

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { display_name: "", avatar_id: DEFAULT_AVATAR_ID },
  });

  useEffect(() => {
    if (profile) {
      reset({
        display_name: profile.display_name,
        avatar_id: profile.avatar_id || DEFAULT_AVATAR_ID,
      });
    }
  }, [profile, reset]);

  async function onSubmit(v: FormValues) {
    setOk(false);
    await save.mutateAsync({
      display_name: v.display_name.trim(),
      avatar_id: v.avatar_id,
    });
    setProfileComplete(true);
    if (isOnboarding) {
      navigate("/c", { replace: true });
      return;
    }
    setOk(true);
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
        {t("customer.profile.title")}
      </h1>

      {isOnboarding && (
        <div className="rounded-xl border border-amber-300/60 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {t("customer.profile.onboardingHint")}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("customer.profile.avatar")}</CardTitle>
        </CardHeader>
        <CardContent>
          <Controller
            control={control}
            name="avatar_id"
            render={({ field }) => (
              <AvatarPicker value={field.value} onChange={field.onChange} />
            )}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("customer.profile.detailsHeader")}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1">
              <Label htmlFor="display_name">{t("customer.profile.displayName")}</Label>
              <Input
                id="display_name"
                placeholder={t("customer.profile.displayNamePlaceholder")}
                autoFocus={isOnboarding}
                {...register("display_name")}
              />
              {errors.display_name && (
                <p className="text-xs text-destructive">{errors.display_name.message}</p>
              )}
            </div>
            {ok && <p className="text-sm text-emerald-600">{t("customer.profile.saved")}</p>}
            <Button type="submit" disabled={isSubmitting} className="h-11">
              {isSubmitting
                ? t("customer.profile.savingShort")
                : isOnboarding
                  ? t("customer.profile.saveAndContinue")
                  : t("customer.profile.saveDetails")}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
