import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { useNavigate, useSearchParams } from "react-router-dom";
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

const schema = z.object({
  display_name: z
    .string()
    .min(2, "Display name must be at least 2 characters")
    .max(120, "Display name is too long"),
  avatar_id: z.string().min(1).max(40),
});

type FormValues = z.infer<typeof schema>;

export function CustomerProfilePage() {
  const { data: profile } = useMyCustomerProfile();
  const save = useSaveCustomerProfile();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const isOnboarding = params.get("onboarding") === "1";
  const setProfileComplete = useAuthStore((s) => s.setProfileComplete);
  const [ok, setOk] = useState(false);

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
      <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Your profile</h1>

      {isOnboarding && (
        <div className="rounded-xl border border-amber-300/60 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Add a display name so specialists know who they&apos;re working with. This is
          how you&apos;ll appear on every project you post.
        </div>
      )}

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
          <CardTitle className="text-base font-medium">Customer details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1">
              <Label htmlFor="display_name">Display name</Label>
              <Input
                id="display_name"
                placeholder="e.g. Acme Inc."
                autoFocus={isOnboarding}
                {...register("display_name")}
              />
              {errors.display_name && (
                <p className="text-xs text-destructive">{errors.display_name.message}</p>
              )}
            </div>
            {ok && <p className="text-sm text-emerald-600">Profile saved.</p>}
            <Button type="submit" disabled={isSubmitting} className="h-11">
              {isSubmitting
                ? "Saving…"
                : isOnboarding
                  ? "Save and continue"
                  : "Save details"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
