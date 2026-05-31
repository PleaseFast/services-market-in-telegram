import { useEffect, useMemo, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { AvatarPicker } from "@/components/avatar/AvatarPicker";
import { CATEGORIES, categoryLabel, clampCategory } from "@/lib/categories";
import { DEFAULT_AVATAR_ID } from "@/lib/avatars";
import { useAuthStore } from "@/stores/auth";
import { useMyProfile, useSaveProfile } from "../api";
import { TimelineSection } from "../components/timeline/TimelineSection";
import { ServicesEditor } from "../components/services/ServicesEditor";
import { ServicesBlock } from "../components/services/ServicesBlock";

type FormValues = {
  full_name: string;
  age: number;
  categories: Array<(typeof CATEGORIES)[number]>;
  years_experience: number;
  bio: string;
  avatar_id: string;
};

export function SpecialistProfilePage() {
  const { t } = useTranslation();
  const { data: profile } = useMyProfile();
  const save = useSaveProfile();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const isOnboarding = params.get("onboarding") === "1";
  const setProfileComplete = useAuthStore((s) => s.setProfileComplete);
  const [ok, setOk] = useState(false);
  const [editingServices, setEditingServices] = useState(false);

  const schema = useMemo(
    () =>
      z.object({
        full_name: z.string().min(2),
        age: z.coerce.number().int().min(14).max(120),
        categories: z
          .array(z.enum(CATEGORIES))
          .min(1, t("specialist.profile.pickAtLeastOne")),
        years_experience: z.coerce.number().int().min(0).max(80),
        bio: z.string().min(1, t("specialist.profile.bioRequired")).max(4000),
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
    defaultValues: {
      bio: "",
      years_experience: 0,
      categories: [],
      avatar_id: DEFAULT_AVATAR_ID,
    } as Partial<FormValues> as FormValues,
  });

  useEffect(() => {
    if (profile) {
      reset({
        full_name: profile.full_name,
        age: profile.age,
        categories: (profile.categories ?? []).map(clampCategory),
        years_experience: profile.years_experience,
        bio: profile.bio,
        avatar_id: profile.avatar_id || DEFAULT_AVATAR_ID,
      });
    }
  }, [profile, reset]);

  async function onSubmit(v: FormValues) {
    setOk(false);
    await save.mutateAsync({
      full_name: v.full_name,
      age: v.age,
      categories: v.categories,
      years_experience: v.years_experience,
      bio: v.bio,
      avatar_id: v.avatar_id,
    });
    setProfileComplete(true);
    if (isOnboarding) {
      navigate("/s/feed", { replace: true });
      return;
    }
    setOk(true);
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
        {t("specialist.profile.title")}
      </h1>

      {isOnboarding && (
        <div className="rounded-xl border border-amber-300/60 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {t("specialist.profile.onboardingHint")}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("specialist.profile.avatar")}</CardTitle>
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
          <CardTitle className="text-base font-medium">{t("specialist.profile.details")}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1">
              <Label htmlFor="full_name">{t("specialist.profile.fullName")}</Label>
              <Input id="full_name" {...register("full_name")} />
              {errors.full_name && (
                <p className="text-xs text-destructive">{errors.full_name.message}</p>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label htmlFor="age">{t("specialist.profile.age")}</Label>
                <Input id="age" type="number" inputMode="numeric" {...register("age")} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="years_experience">{t("specialist.profile.yearsExperience")}</Label>
                <Input
                  id="years_experience"
                  type="number"
                  inputMode="numeric"
                  {...register("years_experience")}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>{t("specialist.profile.specializations")}</Label>
              <p className="text-xs text-muted-foreground">{t("specialist.profile.specializationsHint")}</p>
              <Controller
                control={control}
                name="categories"
                render={({ field }) => {
                  const selected = new Set<(typeof CATEGORIES)[number]>(field.value ?? []);
                  function toggle(cat: (typeof CATEGORIES)[number], checked: boolean) {
                    const next = new Set(selected);
                    if (checked) next.add(cat);
                    else next.delete(cat);
                    field.onChange(Array.from(next));
                  }
                  return (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {CATEGORIES.map((c) => {
                        const checked = selected.has(c);
                        return (
                          <label
                            key={c}
                            className={`flex items-center gap-2 rounded-lg border px-3 py-2 cursor-pointer text-sm ${
                              checked
                                ? "border-foreground/60 bg-muted"
                                : "border-input hover:bg-muted/40"
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={(e) => toggle(c, e.target.checked)}
                              className="h-4 w-4"
                            />
                            <span>{categoryLabel(c)}</span>
                          </label>
                        );
                      })}
                    </div>
                  );
                }}
              />
              {errors.categories && (
                <p className="text-xs text-destructive">{errors.categories.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="bio">{t("specialist.profile.bio")}</Label>
              <Textarea id="bio" rows={5} {...register("bio")} />
              {errors.bio && (
                <p className="text-xs text-destructive">{errors.bio.message}</p>
              )}
            </div>
            {ok && <p className="text-sm text-emerald-600">{t("specialist.profile.saved")}</p>}
            <Button type="submit" disabled={isSubmitting} className="h-11">
              {isSubmitting
                ? t("specialist.profile.savingShort")
                : isOnboarding
                  ? t("specialist.profile.saveAndContinue")
                  : t("specialist.profile.saveDetails")}
            </Button>
          </form>
        </CardContent>
      </Card>

      {profile && !isOnboarding && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
            <CardTitle className="text-base font-medium">
              {t("specialist.profile.servicesHeader")}
            </CardTitle>
            {!editingServices ? (
              <Button
                variant="outline"
                size="sm"
                className="h-9"
                onClick={() => setEditingServices(true)}
              >
                {t("specialist.profile.servicesEdit")}
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                className="h-9"
                onClick={() => setEditingServices(false)}
              >
                {t("specialist.profile.servicesDone")}
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {editingServices ? (
              <ServicesEditor
                primaryCategory={profile.categories?.[0] ?? "Other"}
                selected={profile.services}
                onSaved={() => setEditingServices(false)}
              />
            ) : (
              <ServicesBlock services={profile.services} />
            )}
          </CardContent>
        </Card>
      )}

      {profile && !isOnboarding && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium">
              {t("specialist.profile.experienceHeader")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-8">
            <TimelineSection
              kind="work"
              title={t("specialist.profile.timelineWork")}
              addLabel={t("specialist.profile.addWork")}
              currentToggleLabel={t("specialist.profile.currentWork")}
              items={profile.timeline.work}
            />
            <TimelineSection
              kind="education"
              title={t("specialist.profile.timelineEducation")}
              addLabel={t("specialist.profile.addEducation")}
              currentToggleLabel={t("specialist.profile.currentStudy")}
              items={profile.timeline.education}
            />
            <TimelineSection
              kind="achievement"
              title={t("specialist.profile.timelineAchievements")}
              addLabel={t("specialist.profile.addAchievement")}
              currentToggleLabel={t("specialist.profile.currentPresent")}
              items={profile.timeline.achievement}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
