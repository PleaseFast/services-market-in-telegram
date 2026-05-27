import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useCreateProject, useTemplates } from "@/features/projects/api";
import { useAuthStore } from "@/stores/auth";
import { groupByCategory } from "@/lib/templates";
import {
  clearPendingProject,
  loadPendingProject,
  savePendingProject,
  type PendingProjectValues,
} from "@/lib/pendingProject";
import type { ProjectTemplate } from "@/features/projects/types";

const schema = z.object({
  title: z.string().min(4, "At least 4 characters"),
  description: z.string().min(10, "At least 10 characters"),
  budget: z.coerce.number().min(0),
  currency: z.string().length(3).default("USD"),
  deadline: z.string().optional().or(z.literal("")),
  template_id: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

const DEFAULT_VISIBLE_PER_CATEGORY = 3;

export function CreateProject() {
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const { data: templates } = useTemplates();
  const create = useCreateProject();
  const { user, accessToken } = useAuthStore();
  const isAuthed = !!accessToken && !!user;
  const [err, setErr] = useState<string | null>(null);
  const autosubmitFiredRef = useRef(false);
  const descriptionRef = useRef<HTMLTextAreaElement | null>(null);
  // Tracks the title we last wrote on the user's behalf from a template. If
  // the title field ever diverges from this value while a template is
  // attached, we treat that as the user customizing the project and detach
  // the template (clear template_id + suggested brief).
  const templateAppliedTitleRef = useRef<string | null>(null);

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
  const titleValue = watch("title") ?? "";
  const descriptionValue = watch("description") ?? "";

  const [suggestedBrief, setSuggestedBrief] = useState<string | null>(null);
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});

  const grouped = useMemo(() => groupByCategory(templates ?? []), [templates]);

  // RHF's register handles the textarea ref via {...register("description")}; we
  // also need our own ref for focusing after accepting the suggestion. Compose
  // both into one ref callback.
  const descriptionRegister = register("description");
  const setDescriptionRef = useCallback(
    (node: HTMLTextAreaElement | null) => {
      descriptionRef.current = node;
      descriptionRegister.ref(node);
    },
    [descriptionRegister],
  );

  function pickTemplate(t: ProjectTemplate) {
    // Picking a template means switching project context entirely: title is
    // always replaced with the template title, and the Details textarea is
    // fully cleared so the previous template's brief (or any manual text)
    // doesn't bleed into the new context. The suggestion flow then re-arms
    // automatically because the textarea is empty again.
    //
    // We also stamp the just-applied title into a ref. The detach effect
    // below uses it to tell "this title came from a template" apart from
    // "the user edited the title", and clears template_id on user edits.
    templateAppliedTitleRef.current = t.title;
    setValue("template_id", t.id, { shouldDirty: true });
    setValue("title", t.title, { shouldDirty: true, shouldValidate: true });
    setValue("description", "", { shouldDirty: true, shouldValidate: false });
    setSuggestedBrief(t.description_template);
  }

  function acceptSuggestion() {
    if (!suggestedBrief) return;
    setValue("description", suggestedBrief, {
      shouldDirty: true,
      shouldValidate: true,
    });
    // Move the cursor to the end and refocus.
    requestAnimationFrame(() => {
      const node = descriptionRef.current;
      if (!node) return;
      node.focus();
      const end = node.value.length;
      node.setSelectionRange(end, end);
    });
  }

  function handleDescriptionKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key !== "Tab") return;
    if (e.shiftKey || e.altKey || e.metaKey || e.ctrlKey) return;
    if (!suggestedBrief) return;
    if ((e.currentTarget.value ?? "").length > 0) return;
    e.preventDefault();
    acceptSuggestion();
  }

  // Apply ?template_id from the URL (used by the landing page category grid).
  // Same context-switch semantics as picking a template inline.
  useEffect(() => {
    const tid = params.get("template_id");
    if (!tid || !templates) return;
    const t = templates.find((x) => x.id === tid);
    if (!t) return;
    templateAppliedTitleRef.current = t.title;
    setValue("template_id", t.id);
    setValue("title", t.title);
    setValue("description", "");
    setSuggestedBrief(t.description_template);
  }, [params, templates, setValue]);

  // Rehydrate pending form from sessionStorage on mount.
  useEffect(() => {
    const pending = loadPendingProject();
    if (pending) {
      reset({ ...pending.values });
      // If the rehydrated draft is attached to a template, treat its title as
      // the template-applied title so editing it correctly detaches the
      // template (rather than detaching immediately on mount).
      if (pending.values.template_id) {
        templateAppliedTitleRef.current = pending.values.title ?? null;
      }
    }
  }, [reset]);

  // Apply ?title= from the URL — used by the landing-page search input, which
  // routes here as a "start a project request" entry point. Precedence:
  //   1. ?template_id wins (full template context-switch handled above).
  //   2. A rehydrated pending draft with a title wins (user already has work).
  //   3. Otherwise, prefill the title from ?title= and strip it from the URL
  //      so it doesn't re-apply on later navigation.
  useEffect(() => {
    const t = params.get("title");
    if (!t) return;
    if (params.get("template_id")) return;
    const pending = loadPendingProject();
    if (pending && (pending.values.title ?? "").length > 0) return;
    setValue("title", t, { shouldDirty: true, shouldValidate: true });
    const next = new URLSearchParams(params);
    next.delete("title");
    setParams(next, { replace: true });
  }, [params, setParams, setValue]);

  // Detach the template when the user edits the inherited title. Runs after
  // every title or template_id change; only fires the detach when there is a
  // template attached AND the current title no longer matches what the
  // template put there.
  useEffect(() => {
    if (!templateId) return;
    if (titleValue === templateAppliedTitleRef.current) return;
    templateAppliedTitleRef.current = null;
    setValue("template_id", undefined, { shouldDirty: true });
    // The brief suggestion is meaningful only while the project is attached
    // to the template that produced it; once we detach, drop the suggestion.
    setSuggestedBrief(null);
  }, [titleValue, templateId, setValue]);

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

  const showSuggestion = suggestedBrief !== null && descriptionValue.trim() === "";

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
              <Textarea
                id="description"
                rows={8}
                {...descriptionRegister}
                ref={setDescriptionRef}
                onKeyDown={handleDescriptionKeyDown}
              />
              {showSuggestion && (
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <button
                    type="button"
                    onClick={acceptSuggestion}
                    className="rounded-full border px-3 py-1 text-xs hover:bg-muted"
                  >
                    Insert suggested brief
                  </button>
                  <span className="text-xs text-muted-foreground">
                    or press <kbd className="rounded border px-1 py-px text-[10px] font-medium">Tab</kbd>
                  </span>
                </div>
              )}
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

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Pick a template (optional)</CardTitle>
          <CardDescription>Need a starting point? Picking a template replaces your title and clears the brief so you can start from a popular request.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-5">
            {grouped.map(({ category, items }) => {
              const expanded = expandedCategories[category] ?? false;
              const visible = expanded ? items : items.slice(0, DEFAULT_VISIBLE_PER_CATEGORY);
              const hiddenCount = items.length - visible.length;
              return (
                <div key={category} className="space-y-2">
                  <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    {category}
                    <span className="ml-2 text-muted-foreground/60 normal-case tracking-normal">
                      {items.length}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {visible.map((t) => (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => pickTemplate(t)}
                        className={
                          templateId === t.id
                            ? "rounded-full border px-3 py-1 text-xs bg-primary text-primary-foreground border-primary"
                            : "rounded-full border px-3 py-1 text-xs hover:bg-muted"
                        }
                      >
                        {t.title}
                      </button>
                    ))}
                    {items.length > DEFAULT_VISIBLE_PER_CATEGORY && (
                      <button
                        type="button"
                        onClick={() =>
                          setExpandedCategories((s) => ({ ...s, [category]: !expanded }))
                        }
                        className="rounded-full border border-dashed px-3 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
                      >
                        {expanded ? "Show less" : `+${hiddenCount} more`}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
