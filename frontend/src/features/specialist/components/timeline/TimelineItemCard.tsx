import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Pencil, Trash2, ArrowUp, ArrowDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  useDeleteTimelineItem,
  useMoveTimelineItem,
} from "@/features/specialist/api";
import type { TimelineItem, TimelineKind } from "@/features/projects/types";
import { TimelineItemForm } from "./TimelineItemForm";

export function TimelineItemCard({
  item,
  currentToggleLabel,
  kind,
  isFirst,
  isLast,
}: {
  item: TimelineItem;
  currentToggleLabel: string;
  kind: TimelineKind;
  isFirst: boolean;
  isLast: boolean;
}) {
  const { t } = useTranslation();
  const [editing, setEditing] = useState(false);
  const del = useDeleteTimelineItem();
  const move = useMoveTimelineItem();

  function formatYears(it: TimelineItem): string {
    if (it.is_current) return t("specialist.timeline.yearsRangePresent", { start: it.start_year });
    if (it.end_year === null) return `${it.start_year}`;
    if (it.start_year === it.end_year) return `${it.start_year}`;
    return `${it.start_year} – ${it.end_year}`;
  }

  if (editing) {
    return (
      <TimelineItemForm
        kind={kind}
        currentToggleLabel={currentToggleLabel}
        existing={item}
        onSaved={() => setEditing(false)}
        onCancel={() => setEditing(false)}
      />
    );
  }

  return (
    <Card>
      <CardContent className="p-4 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="font-medium leading-tight">{item.title}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{formatYears(item)}</p>
          </div>
          <div className="flex shrink-0 gap-1">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => move.mutate({ id: item.id, direction: "up" })}
              disabled={isFirst || move.isPending}
              aria-label={t("specialist.timeline.moveUp")}
              className="h-9 w-9"
            >
              <ArrowUp className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => move.mutate({ id: item.id, direction: "down" })}
              disabled={isLast || move.isPending}
              aria-label={t("specialist.timeline.moveDown")}
              className="h-9 w-9"
            >
              <ArrowDown className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => setEditing(true)}
              aria-label={t("specialist.timeline.edit")}
              className="h-9 w-9"
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => {
                if (confirm(t("specialist.timeline.confirmDelete"))) del.mutate(item.id);
              }}
              disabled={del.isPending}
              aria-label={t("specialist.timeline.delete")}
              className="h-9 w-9"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        {item.description && (
          <p className="text-sm text-muted-foreground whitespace-pre-line">{item.description}</p>
        )}
      </CardContent>
    </Card>
  );
}
