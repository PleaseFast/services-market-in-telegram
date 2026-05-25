import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useMyProfile, useSaveProfile } from "../api";

const schema = z.object({
  full_name: z.string().min(2),
  age: z.coerce.number().int().min(14).max(120),
  category: z.string().min(2),
  years_experience: z.coerce.number().int().min(0).max(80),
  bio: z.string().max(4000).default(""),
  avatar_url: z.string().url().optional().or(z.literal("")),
});

type FormValues = z.infer<typeof schema>;

export function SpecialistProfilePage() {
  const { data: profile } = useMyProfile();
  const save = useSaveProfile();
  const [ok, setOk] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { bio: "", years_experience: 0 } as Partial<FormValues> as FormValues,
  });

  useEffect(() => {
    if (profile) {
      reset({
        full_name: profile.full_name,
        age: profile.age,
        category: profile.category,
        years_experience: profile.years_experience,
        bio: profile.bio,
        avatar_url: profile.avatar_url ?? "",
      });
    }
  }, [profile, reset]);

  async function onSubmit(v: FormValues) {
    setOk(false);
    await save.mutateAsync({
      ...v,
      avatar_url: v.avatar_url || null,
      workplaces: profile?.workplaces.map((w) => ({ title: w.title, company: w.company, period: w.period })) ?? [],
      portfolio_links: profile?.portfolio_links.map((p) => ({ url: p.url, label: p.label })) ?? [],
    });
    setOk(true);
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Your specialist profile</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="full_name">Full name</Label>
              <Input id="full_name" {...register("full_name")} />
              {errors.full_name && <p className="text-xs text-destructive">{errors.full_name.message}</p>}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1">
                <Label htmlFor="age">Age</Label>
                <Input id="age" type="number" {...register("age")} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="category">Category</Label>
                <Input id="category" placeholder="Backend, Frontend, …" {...register("category")} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="years_experience">Years experience</Label>
                <Input id="years_experience" type="number" {...register("years_experience")} />
              </div>
            </div>
            <div className="space-y-1">
              <Label htmlFor="bio">Bio</Label>
              <Textarea id="bio" rows={5} {...register("bio")} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="avatar_url">Avatar URL</Label>
              <Input id="avatar_url" placeholder="https://…" {...register("avatar_url")} />
            </div>
            {ok && <p className="text-sm text-emerald-600">Profile saved.</p>}
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving…" : "Save"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
