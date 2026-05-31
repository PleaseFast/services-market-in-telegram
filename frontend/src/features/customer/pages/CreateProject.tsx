import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { z } from "zod";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { useCreateProject, useTemplates } from "@/features/projects/api";
import { useAuthStore } from "@/stores/auth";
import { groupByCategory } from "@/lib/templates";
import { CATEGORIES, categoryLabel, clampCategory, suggestCategory } from "@/lib/categories";
import {
  clearPendingProject,
  loadPendingProject,
  savePendingProject,
  type PendingProjectValues,
} from "@/lib/pendingProject";
import type { ProjectTemplate } from "@/features/projects/types";
import { ApiError } from "@/lib/api";

type FormValues = {
  title: string;
  description: string;
  budget: number;
  currency: string;
  deadline?: string;
  template_id?: string;
  category: (typeof CATEGORIES)[number];
};

const DEFAULT_VISIBLE_PER_CATEGORY = 3;

export function CreateProject() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const { data: templates } = useTemplates();
  const create = useCreateProject();
  const { user, accessToken } = useAuthStore();
  const isAuthed = !!accessToken && !!user;
  const [err, setErr] = useState<string | null>(null);
  const autosubmitFiredRef = useRef(false);
  const descriptionRef = useRef<HTMLTextAreaElement | null>(null);
  const templateAppliedTitleRef = useRef<string | null>(null);

  const schema = useMemo(
    () =>
      z.object({
        title: z.string().min(4, t("validation.title.min", { count: 4 })),
        description: z.string().min(10, t("validation.description.min", { count: 10 })),
        budget: z.coerce.number().min(0),
        currency: z.string().length(3).default("USD"),
        deadline: z.string().optional().or(z.literal("")),
        template_id: z.string().optional(),
        category: z.enum(CATEGORIES),
      }),
    [t],
  );

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { currency: "USD", category: "Other" },
  });

  const templateId = watch("template_id");
  const titleValue = watch("title") ?? "";
  const descriptionValue = watch("description") ?? "";
  const categoryValue = watch("category");

  const [suggestedBrief, setSuggestedBrief] = useState<string | null>(null);
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});
  const [categoryTouched, setCategoryTouched] = useState(false);

  const grouped = useMemo(() => groupByCategory(templates ?? []), [templates]);

  const descriptionRegister = register("description");
  const setDescriptionRef = useCallback(
    (node: HTMLTextAreaElement | null) => {
      descriptionRef.current = node;
      descriptionRegister.ref(node);
    },
    [descriptionRegister],
  );

  function pickTemplate(tpl: ProjectTemplate) {
    templateAppliedTitleRef.current = tpl.title;
    setValue("template_id", tpl.id, { shouldDirty: true });
    setValue("title", tpl.title, { shouldDirty: true, shouldValidate: true });
    setValue("description", "", { shouldDirty: true, shouldValidate: false });
    setValue("category", clampCategory(tpl.category), { shouldDirty: true, shouldValidate: true });
    setCategoryTouched(true);
    setSuggestedBrief(tpl.description_template);
  }

  function acceptSuggestion() {
    if (!suggestedBrief) return;
    setValue("description", suggestedBrief, {
      shouldDirty: true,
      shouldValidate: true,
    });
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

  useEffect(() => {
    const tid = params.get("template_id");
    if (!tid || !templates) return;
    const tpl = templates.find((x) => x.id === tid);
    if (!tpl) return;
    templateAppliedTitleRef.current = tpl.title;
    setValue("template_id", tpl.id);
    setValue("title", tpl.title);
    setValue("description", "");
    setValue("category", clampCategory(tpl.category));
    setCategoryTouched(true);
    setSuggestedBrief(tpl.description_template);
  }, [params, templates, setValue]);

  useEffect(() => {
    const pending = loadPendingProject();
    if (pending) {
      reset({
        ...pending.values,
        category: clampCategory(pending.values.category),
      } as Partial<FormValues> as FormValues);
      if (pending.values.template_id) {
        templateAppliedTitleRef.current = pending.values.title ?? null;
      }
      if (pending.values.category) setCategoryTouched(true);
    }
  }, [reset]);

  useEffect(() => {
    if (categoryTouched) return;
    const suggested = suggestCategory(titleValue, descriptionValue);
    if (suggested !== categoryValue) {
      setValue("category", suggested, { shouldDirty: false, shouldValidate: false });
    }
  }, [titleValue, descriptionValue, categoryTouched, categoryValue, setValue]);

  useEffect(() => {
    const titleParam = params.get("title");
    if (!titleParam) return;
    if (params.get("template_id")) return;
    const pending = loadPendingProject();
    if (pending && (pending.values.title ?? "").length > 0) return;
    setValue("title", titleParam, { shouldDirty: true, shouldValidate: true });
    const next = new URLSearchParams(params);
    next.delete("title");
    setParams(next, { replace: true });
  }, [params, setParams, setValue]);

  useEffect(() => {
    if (!templateId) return;
    if (titleValue === templateAppliedTitleRef.current) return;
    templateAppliedTitleRef.current = null;
    setValue("template_id", undefined, { shouldDirty: true });
    setSuggestedBrief(null);
  }, [titleValue, templateId, setValue]);

  useEffect(() => {
    if (autosubmitFiredRef.current) return;
    if (params.get("autosubmit") !== "1") return;
    const pending = loadPendingProject();
    if (!pending) {
      params.delete("autosubmit");
      setParams(params, { replace: true });
      return;
    }
    if (!isAuthed) return;

    if (user!.role !== "customer") {
      setErr(t("customer.create.wrongRole"));
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
          category: pending.values.category ?? null,
          publish: true,
        });
        clearPendingProject();
        nav(`/c/projects/${p.id}`, { replace: true });
      } catch (e: unknown) {
        autosubmitFiredRef.current = false;
        setErr(e instanceof ApiError ? e.localized() : (e as Error).message);
        params.delete("autosubmit");
        setParams(params, { replace: true });
      }
    })();
  }, [params, setParams, isAuthed, user, create, nav, t]);

  async function onSubmit(values: FormValues, publish: boolean) {
    setErr(null);

    if (publish && !isAuthed) {
      const payload: PendingProjectValues = {
        title: values.title,
        description: values.description,
        budget: values.budget,
        currency: values.currency,
        deadline: values.deadline,
        template_id: values.template_id,
        category: values.category,
      };
      savePendingProject(payload);
      useAuthStore.getState().exitGuest();
      nav("/register?next=/c/new&role=customer&autosubmit=1");
      return;
    }

    if (!isAuthed) {
      const payload: PendingProjectValues = {
        title: values.title,
        description: values.description,
        budget: values.budget,
        currency: values.currency,
        deadline: values.deadline,
        template_id: values.template_id,
        category: values.category,
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
        category: values.category,
        publish,
      });
      clearPendingProject();
      nav(`/c/projects/${p.id}`);
    } catch (e: unknown) {
      setErr(e instanceof ApiError ? e.localized() : (e as Error).message);
    }
  }

  if (
    params.get("autosubmit") === "1" &&
    isAuthed &&
    user!.role === "customer" &&
    !err
  ) {
    return (
      <div className="max-w-3xl mx-auto py-16 text-center">
        <p className="text-muted-foreground text-sm">{t("customer.create.publishing")}</p>
      </div>
    );
  }

  const showSuggestion = suggestedBrief !== null && descriptionValue.trim() === "";

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {!isAuthed && (
        <Card className="border-dashed">
          <CardContent className="pt-6 text-sm text-muted-foreground">
            {t("customer.create.anonHint", { publishWord: t("customer.create.publishWord") })}
            <span className="ml-2">
              {t("customer.create.alreadyHaveAccount")}{" "}
              <Link to="/login?next=/c/new" className="text-foreground underline-offset-4 hover:underline">
                {t("customer.create.signIn")}
              </Link>
            </span>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("customer.create.describe")}</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="title">{t("customer.create.title")}</Label>
              <Input id="title" {...register("title")} />
              {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="category">{t("customer.create.category")}</Label>
              <Select
                id="category"
                {...register("category", {
                  onChange: () => setCategoryTouched(true),
                })}
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {categoryLabel(c)}
                  </option>
                ))}
              </Select>
              {!categoryTouched && (
                <p className="text-xs text-muted-foreground">{t("customer.create.categoryHint")}</p>
              )}
              {errors.category && (
                <p className="text-xs text-destructive">{errors.category.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="description">{t("customer.create.details")}</Label>
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
                    {t("customer.create.suggestionInsert")}
                  </button>
                  <span className="text-xs text-muted-foreground">
                    {t("customer.create.suggestionOrTab")}{" "}
                    <kbd className="rounded border px-1 py-px text-[10px] font-medium">Tab</kbd>
                  </span>
                </div>
              )}
              {errors.description && <p className="text-xs text-destructive">{errors.description.message}</p>}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="budget">{t("customer.create.budget")}</Label>
                <Input id="budget" type="number" {...register("budget")} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="currency">{t("customer.create.currency")}</Label>
                <Input id="currency" maxLength={3} {...register("currency")} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="deadline">{t("customer.create.deadline")}</Label>
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
                {t("customer.create.saveDraft")}
              </Button>
              <Button
                type="button"
                disabled={isSubmitting}
                onClick={handleSubmit((v) => onSubmit(v, true))}
              >
                {isAuthed ? t("customer.create.publish") : t("customer.create.publishSignIn")}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">{t("customer.create.templatesTitle")}</CardTitle>
          <CardDescription>{t("customer.create.templatesHint")}</CardDescription>
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
                    {categoryLabel(category)}
                    <span className="ml-2 text-muted-foreground/60 normal-case tracking-normal">
                      {items.length}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {visible.map((tpl) => (
                      <button
                        key={tpl.id}
                        type="button"
                        onClick={() => pickTemplate(tpl)}
                        className={
                          templateId === tpl.id
                            ? "rounded-full border px-3 py-1 text-xs bg-primary text-primary-foreground border-primary"
                            : "rounded-full border px-3 py-1 text-xs hover:bg-muted"
                        }
                      >
                        {tpl.title}
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
                        {expanded
                          ? t("customer.create.showLess")
                          : t("customer.create.showMore", { count: hiddenCount })}
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
