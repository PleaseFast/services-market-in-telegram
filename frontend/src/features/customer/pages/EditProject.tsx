import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { useProject, useUpdateProject } from "@/features/projects/api";
import { CATEGORIES, clampCategory } from "@/lib/categories";

const schema = z.object({
  title: z.string().min(4, "At least 4 characters"),
  description: z.string().min(10, "At least 10 characters"),
  budget: z.coerce.number().min(0),
  currency: z.string().length(3),
  deadline: z.string().optional().or(z.literal("")),
  category: z.enum(CATEGORIES),
});

type FormValues = z.infer<typeof schema>;

export function EditProject() {
  const { id } = useParams<{ id: string }>();
  const nav = useNavigate();
  const { data: project, isLoading } = useProject(id);
  const update = useUpdateProject(id);
  const [err, setErr] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { currency: "USD", category: "Other" },
  });

  useEffect(() => {
    if (!project) return;
    reset({
      title: project.title,
      description: project.description,
      budget: Number(project.budget),
      currency: project.currency,
      deadline: project.deadline ?? "",
      category: clampCategory(project.category),
    });
  }, [project, reset]);

  if (isLoading || !project) {
    return <p className="text-muted-foreground text-sm">Loading…</p>;
  }

  const editable = ["draft", "open", "paused"].includes(project.status);
  if (!editable) {
    return (
      <div className="max-w-3xl mx-auto">
        <p className="text-sm text-muted-foreground">
          This project can no longer be edited (status: {project.status}).
        </p>
      </div>
    );
  }

  async function onSubmit(values: FormValues) {
    setErr(null);
    try {
      await update.mutateAsync({
        title: values.title,
        description: values.description,
        budget: values.budget,
        currency: values.currency,
        deadline: values.deadline || null,
        category: values.category,
      });
      nav(`/c/projects/${id}`);
    } catch (e: unknown) {
      setErr((e as Error).message);
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Edit project</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-1.5">
              <Label htmlFor="title">Title</Label>
              <Input id="title" {...register("title")} />
              {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
            </div>
            <div className="space-y-1.5">
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
            <div className="space-y-1.5">
              <Label htmlFor="description">Details</Label>
              <Textarea id="description" rows={8} {...register("description")} />
              {errors.description && (
                <p className="text-xs text-destructive">{errors.description.message}</p>
              )}
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
                onClick={() => nav(`/c/projects/${id}`)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                Save changes
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
