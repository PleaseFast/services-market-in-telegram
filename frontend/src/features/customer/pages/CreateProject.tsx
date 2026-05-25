import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useCreateProject, useTemplates } from "@/features/projects/api";

const schema = z.object({
  title: z.string().min(4),
  description: z.string().min(10),
  budget: z.coerce.number().min(0),
  currency: z.string().length(3).default("USD"),
  deadline: z.string().optional().or(z.literal("")),
  template_id: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function CreateProject() {
  const nav = useNavigate();
  const { data: templates } = useTemplates();
  const create = useCreateProject();
  const [err, setErr] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { currency: "USD" },
  });

  const templateId = watch("template_id");

  async function onSubmit(values: FormValues, publish: boolean) {
    setErr(null);
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
      nav(`/c/projects/${p.id}`);
    } catch (e: unknown) {
      setErr((e as Error).message);
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Pick a template (optional)</CardTitle>
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
                    ? "rounded-full border px-3 py-1 text-xs bg-primary text-primary-foreground"
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
          <CardTitle>Describe your project</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="title">Title</Label>
              <Input id="title" {...register("title")} />
              {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
            </div>
            <div className="space-y-1">
              <Label htmlFor="description">Details</Label>
              <Textarea id="description" rows={8} {...register("description")} />
              {errors.description && <p className="text-xs text-destructive">{errors.description.message}</p>}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1">
                <Label htmlFor="budget">Budget</Label>
                <Input id="budget" type="number" {...register("budget")} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="currency">Currency</Label>
                <Input id="currency" maxLength={3} {...register("currency")} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="deadline">Deadline</Label>
                <Input id="deadline" type="date" {...register("deadline")} />
              </div>
            </div>
            {err && <p className="text-sm text-destructive">{err}</p>}
            <div className="flex gap-2">
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
                Publish
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
