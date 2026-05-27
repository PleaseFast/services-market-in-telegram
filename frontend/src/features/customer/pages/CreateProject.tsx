import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useCreateProject, useTemplates } from "@/features/projects/api";
import { useAuthStore } from "@/stores/auth";
import {
  clearPendingProject,
  loadPendingProject,
  savePendingProject,
  type PendingProjectValues,
} from "@/lib/pendingProject";

const schema = z.object({
  title: z.string().min(4, "At least 4 characters"),
  description: z.string().min(10, "At least 10 characters"),
  budget: z.coerce.number().min(0),
  currency: z.string().length(3).default("USD"),
  deadline: z.string().optional().or(z.literal("")),
  template_id: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function CreateProject() {
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const { data: templates } = useTemplates();
  const create = useCreateProject();
  const { user, accessToken } = useAuthStore();
  const isAuthed = !!accessToken && !!user;
  const [err, setErr] = useState<string | null>(null);
  const autosubmitFiredRef = useRef(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { currency: "USD" },
  });

  const templateId = watch("template_id");

  // Apply ?template_id from the URL (used by the landing page category grid).
  useEffect(() => {
    const tid = params.get("template_id");
    if (!tid || !templates) return;
    const t = templates.find((x) => x.id === tid);
    if (!t) return;
    setValue("template_id", t.id);
    setValue("title", t.title);
    setValue("description", t.description_template);
  }, [params, templates, setValue]);

  // Rehydrate pending form from sessionStorage on mount.
  useEffect(() => {
    const pending = loadPendingProject();
    if (pending) {
      reset({ ...pending.values });
    }
  }, [reset]);

  // Auto-submit after returning from auth, if intent was publish.
  useEffect(() => {
    if (autosubmitFiredRef.current) return;
    if (params.get("autosubmit") !== "1") return;
    const pending = loadPendingProject();
    if (!pending) {
      // Nothing to auto-submit — clean URL and stop.
      params.delete("autosubmit");
      setParams(params, { replace: true });
      return;
    }
    if (!isAuthed) return; // wait for auth bootstrap

    if (user!.role !== "customer") {
      setErr(
        "You're signed in as a specialist, but only customers can publish projects. " +
          "Sign out and create a customer account to publish this draft.",
      );
      clearPendingProject();
      params.delete("autosubmit");
      setParams(params, { replace: true });
      return;
    }

    autosubmitFiredRef.current = true;
    (async () => {
      try {
        const p = await create.mutateAsync({
          title: pending.values.title,
          description: pending.values.description,
          budget: pending.values.budget,
          currency: pending.values.currency,
          deadline: pending.values.deadline || null,
          template_id: pending.values.template_id || null,
          publish: true,
        });
        clearPendingProject();
        nav(`/c/projects/${p.id}`, { replace: true });
      } catch (e: unknown) {
        autosubmitFiredRef.current = false;
        setErr((e as Error).message);
        params.delete("autosubmit");
        setParams(params, { replace: true });
      }
    })();
  }, [params, setParams, isAuthed, user, create, nav]);

  async function onSubmit(values: FormValues, publish: boolean) {
    setErr(null);

    // Delayed auth: if the visitor is anonymous and wants to publish,
    // stash the draft and bounce them to the customer register flow.
    if (publish && !isAuthed) {
      const payload: PendingProjectValues = {
        title: values.title,
        description: values.description,
        budget: values.budget,
        currency: values.currency,
        deadline: values.deadline,
        template_id: values.template_id,
      };
      savePendingProject(payload);
      // Exit guest mode if applicable so the auth flow is clean.
      useAuthStore.getState().exitGuest();
      nav("/register?next=/c/new&role=customer&autosubmit=1");
      return;
    }

    // "Save as draft" requires an account too — same redirect, but no autosubmit.
    if (!isAuthed) {
      const payload: PendingProjectValues = {
        title: values.title,
        description: values.description,
        budget: values.budget,
        currency: values.currency,
        deadline: values.deadline,
        template_id: values.template_id,
      };
      savePendingProject(payload);
      useAuthStore.getState().exitGuest();
      nav("/register?next=/c/new&role=customer");
      return;
    }

    try {
      const p = await create.mutateAsync({
        title: values.title,
        description: values.description,
        budget: values.budget,
        currency: values.currency,
        deadline: values.deadline || null,
        template_id: values.template_id || null,
        publish,
      });
      clearPendingProject();
      nav(`/c/projects/${p.id}`);
    } catch (e: unknown) {
      setErr((e as Error).message);
    }
  }

  // If we're auto-submitting, render a tiny waiting state so the user sees
  // continuity rather than the form briefly re-appearing.
  if (
    params.get("autosubmit") === "1" &&
    isAuthed &&
    user!.role === "customer" &&
    !err
  ) {
    return (
      <div className="max-w-3xl mx-auto py-16 text-center">
        <p className="text-muted-foreground text-sm">Publishing your project…</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {!isAuthed && (
        <Card className="border-dashed">
          <CardContent className="pt-6 text-sm text-muted-foreground">
            You can describe your project without an account. We&apos;ll ask you to sign in only when you click <span className="font-medium text-foreground">Publish</span>.
            <span className="ml-2">
              Already have one?{" "}
              <Link to="/login?next=/c/new" className="text-foreground underline-offset-4 hover:underline">
                Sign in
              </Link>
            </span>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Pick a template (optional)</CardTitle>
          <CardDescription>Start from a popular request, or skip and describe your own.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {templates?.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => {
                  setValue("template_id", t.id);
                  setValue("title", t.title);
                  setValue("description", t.description_template);
                }}
                className={
                  templateId === t.id
                    ? "rounded-full border px-3 py-1 text-xs bg-primary text-primary-foreground border-primary"
                    : "rounded-full border px-3 py-1 text-xs hover:bg-muted"
                }
              >
                {t.title} <Badge tone="outline" className="ml-1">{t.category}</Badge>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Describe your project</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="title">Title</Label>
              <Input id="title" {...register("title")} />
              {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="description">Details</Label>
              <Textarea id="description" rows={8} {...register("description")} />
              {errors.description && <p className="text-xs text-destructive">{errors.description.message}</p>}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="budget">Budget</Label>
                <Input id="budget" type="number" {...register("budget")} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="currency">Currency</Label>
                <Input id="currency" maxLength={3} {...register("currency")} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="deadline">Deadline</Label>
                <Input id="deadline" type="date" {...register("deadline")} />
              </div>
            </div>
            {err && <p className="text-sm text-destructive">{err}</p>}
            <div className="flex gap-2 pt-2">
              <Button
                type="button"
                variant="outline"
                disabled={isSubmitting}
                onClick={handleSubmit((v) => onSubmit(v, false))}
              >
                Save as draft
              </Button>
              <Button
                type="button"
                disabled={isSubmitting}
                onClick={handleSubmit((v) => onSubmit(v, true))}
              >
                {isAuthed ? "Publish" : "Publish — sign in & post"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
