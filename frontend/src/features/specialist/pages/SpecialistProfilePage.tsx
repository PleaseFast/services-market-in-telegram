import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { AvatarPicker } from "@/components/avatar/AvatarPicker";
import { CATEGORIES, clampCategory } from "@/lib/categories";
import { DEFAULT_AVATAR_ID } from "@/lib/avatars";
import { useMyProfile, useSaveProfile } from "../api";
import { TimelineSection } from "../components/timeline/TimelineSection";
import { ServicesEditor } from "../components/services/ServicesEditor";
import { ServicesBlock } from "../components/services/ServicesBlock";

const schema = z.object({
  full_name: z.string().min(2),
  age: z.coerce.number().int().min(14).max(120),
  category: z.enum(CATEGORIES),
  years_experience: z.coerce.number().int().min(0).max(80),
  bio: z.string().max(4000).default(""),
  avatar_id: z.string().min(1).max(40),
});

type FormValues = z.infer<typeof schema>;

export function SpecialistProfilePage() {
  const { data: profile } = useMyProfile();
  const save = useSaveProfile();
  const [ok, setOk] = useState(false);
  const [editingServices, setEditingServices] = useState(false);

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
      avatar_id: DEFAULT_AVATAR_ID,
    } as Partial<FormValues> as FormValues,
  });

  useEffect(() => {
    if (profile) {
      reset({
        full_name: profile.full_name,
        age: profile.age,
        category: clampCategory(profile.category),
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
      category: v.category,
      years_experience: v.years_experience,
      bio: v.bio,
      avatar_id: v.avatar_id,
    });
    setOk(true);
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Your profile</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Avatar</CardTitle>
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
          <CardTitle className="text-base font-medium">Specialist details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1">
              <Label htmlFor="full_name">Full name</Label>
              <Input id="full_name" {...register("full_name")} />
              {errors.full_name && (
                <p className="text-xs text-destructive">{errors.full_name.message}</p>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1">
                <Label htmlFor="age">Age</Label>
                <Input id="age" type="number" inputMode="numeric" {...register("age")} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="category">Category</Label>
                <Select id="category" {...register("category")}>
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </Select>
                {errors.category && (
                  <p className="text-xs text-destructive">{errors.category.message}</p>
                )}
              </div>
              <div className="space-y-1">
                <Label htmlFor="years_experience">Years experience</Label>
                <Input
                  id="years_experience"
                  type="number"
                  inputMode="numeric"
                  {...register("years_experience")}
                />
              </div>
            </div>
            <div className="space-y-1">
              <Label htmlFor="bio">Bio</Label>
              <Textarea id="bio" rows={5} {...register("bio")} />
            </div>
            {ok && <p className="text-sm text-emerald-600">Profile saved.</p>}
            <Button type="submit" disabled={isSubmitting} className="h-11">
              {isSubmitting ? "Saving…" : "Save details"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {profile && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
            <CardTitle className="text-base font-medium">Services and work conditions</CardTitle>
            {!editingServices ? (
              <Button
                variant="outline"
                size="sm"
                className="h-9"
                onClick={() => setEditingServices(true)}
              >
                Edit
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                className="h-9"
                onClick={() => setEditingServices(false)}
              >
                Done
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {editingServices ? (
              <ServicesEditor
                primaryCategory={profile.category}
                selected={profile.services}
                onSaved={() => setEditingServices(false)}
              />
            ) : (
              <ServicesBlock services={profile.services} />
            )}
          </CardContent>
        </Card>
      )}

      {profile && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium">Education and experience</CardTitle>
          </CardHeader>
          <CardContent className="space-y-8">
            <TimelineSection
              kind="work"
              title="Work experience"
              addLabel="Add work experience"
              currentToggleLabel="Currently working here"
              items={profile.timeline.work}
            />
            <TimelineSection
              kind="education"
              title="Education"
              addLabel="Add education"
              currentToggleLabel="Currently studying here"
              items={profile.timeline.education}
            />
            <TimelineSection
              kind="achievement"
              title="Achievements"
              addLabel="Add achievement"
              currentToggleLabel="Present time"
              items={profile.timeline.achievement}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
