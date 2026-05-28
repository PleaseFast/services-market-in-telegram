import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import {
  useCreateTimelineItem,
  usePatchTimelineItem,
  type TimelineItemInput,
} from "@/features/specialist/api";
import type { TimelineItem, TimelineKind } from "@/features/projects/types";

const currentYear = new Date().getFullYear();
const YEAR_FLOOR = 1950;
const YEAR_CEIL = currentYear + 1;

const schema = z
  .object({
    title: z.string().min(2, "At least 2 characters").max(200),
    description: z.string().max(4000).default(""),
    start_year: z.coerce.number().int().min(YEAR_FLOOR).max(YEAR_CEIL),
    end_year: z.union([z.coerce.number().int().min(YEAR_FLOOR).max(YEAR_CEIL), z.literal("")]),
    is_current: z.boolean().default(false),
  })
  .superRefine((v, ctx) => {
    if (!v.is_current && v.end_year === "") {
      ctx.addIssue({
        path: ["end_year"],
        code: z.ZodIssueCode.custom,
        message: "End year is required",
      });
    }
    if (
      !v.is_current &&
      typeof v.end_year === "number" &&
      v.end_year < v.start_year
    ) {
      ctx.addIssue({
        path: ["end_year"],
        code: z.ZodIssueCode.custom,
        message: "End year must be after start year",
      });
    }
  });

type FormValues = z.infer<typeof schema>;

interface TimelineItemFormProps {
  kind: TimelineKind;
  currentToggleLabel: string;
  existing?: TimelineItem;
  onSaved: () => void;
  onCancel?: () => void;
}

export function TimelineItemForm({
  kind,
  currentToggleLabel,
  existing,
  onSaved,
  onCancel,
}: TimelineItemFormProps) {
  const create = useCreateTimelineItem();
  const patch = usePatchTimelineItem();
  const [err, setErr] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: existing?.title ?? "",
      description: existing?.description ?? "",
      start_year: existing?.start_year ?? currentYear,
      end_year: existing?.end_year ?? currentYear,
      is_current: existing?.is_current ?? false,
    },
  });

  const isCurrent = watch("is_current");

  // When the toggle switches on, clear end_year. When it switches off, default
  // back to the current year so the user sees a valid value.
  useEffect(() => {
    if (isCurrent) setValue("end_year", "");
    else if (watch("end_year") === "") setValue("end_year", currentYear);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isCurrent]);

  async function onSubmit(v: FormValues) {
    setErr(null);
    const payload: TimelineItemInput = {
      kind,
      title: v.title,
      description: v.description,
      start_year: v.start_year,
      end_year: v.is_current || v.end_year === "" ? null : (v.end_year as number),
      is_current: v.is_current,
    };
    try {
      if (existing) {
        await patch.mutateAsync({ id: existing.id, patch: payload });
      } else {
        await create.mutateAsync(payload);
      }
      onSaved();
    } catch (e: unknown) {
      setErr((e as Error).message);
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3 rounded-lg border p-4">
      <div className="space-y-1">
        <Label htmlFor={`title-${existing?.id ?? "new"}`}>Title</Label>
        <Input id={`title-${existing?.id ?? "new"}`} {...register("title")} />
        {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
      </div>
      <div className="space-y-1">
        <Label htmlFor={`description-${existing?.id ?? "new"}`}>Description</Label>
        <Textarea
          id={`description-${existing?.id ?? "new"}`}
          rows={3}
          {...register("description")}
        />
      </div>
      <div className="grid grid-cols-2 gap-2 min-w-0">
        <div className="space-y-1">
          <Label htmlFor={`start-${existing?.id ?? "new"}`}>Start year</Label>
          <Input
            id={`start-${existing?.id ?? "new"}`}
            type="number"
            inputMode="numeric"
            min={YEAR_FLOOR}
            max={YEAR_CEIL}
            {...register("start_year")}
          />
          {errors.start_year && (
            <p className="text-xs text-destructive">{errors.start_year.message}</p>
          )}
        </div>
        <div className="space-y-1">
          <Label htmlFor={`end-${existing?.id ?? "new"}`}>End year</Label>
          <Input
            id={`end-${existing?.id ?? "new"}`}
            type="number"
            inputMode="numeric"
            min={YEAR_FLOOR}
            max={YEAR_CEIL}
            disabled={isCurrent}
            {...register("end_year")}
          />
          {errors.end_year && (
            <p className="text-xs text-destructive">{errors.end_year.message as string}</p>
          )}
        </div>
      </div>
      <div className="flex items-center justify-between gap-2">
        <Label htmlFor={`current-${existing?.id ?? "new"}`} className="cursor-pointer">
          {currentToggleLabel}
        </Label>
        <Controller
          control={control}
          name="is_current"
          render={({ field }) => (
            <Switch
              id={`current-${existing?.id ?? "new"}`}
              checked={field.value}
              onCheckedChange={field.onChange}
            />
          )}
        />
      </div>
      {err && <p className="text-sm text-destructive">{err}</p>}
      <div className="flex gap-2 pt-1">
        <Button type="submit" disabled={isSubmitting} className="h-11">
          {isSubmitting ? "Saving…" : existing ? "Save changes" : "Add"}
        </Button>
        {onCancel && (
          <Button type="button" variant="ghost" onClick={onCancel} className="h-11">
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
