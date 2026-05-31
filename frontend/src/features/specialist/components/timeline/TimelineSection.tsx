import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { TimelineItem, TimelineKind } from "@/features/projects/types";
import { TimelineItemCard } from "./TimelineItemCard";
import { TimelineItemForm } from "./TimelineItemForm";

interface TimelineSectionProps {
  kind: TimelineKind;
  title: string;
  addLabel: string;
  currentToggleLabel: string;
  items: TimelineItem[];
}

export function TimelineSection({
  kind,
  title,
  addLabel,
  currentToggleLabel,
  items,
}: TimelineSectionProps) {
  const { t } = useTranslation();
  const [adding, setAdding] = useState(false);
  const sorted = [...items].sort((a, b) => a.position - b.position);

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-base font-medium">{title}</h3>
        {!adding && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="h-9"
            onClick={() => setAdding(true)}
          >
            <Plus className="h-4 w-4 mr-1" />
            {addLabel}
          </Button>
        )}
      </div>
      <div className="space-y-3">
        {sorted.map((item, idx) => (
          <TimelineItemCard
            key={item.id}
            item={item}
            kind={kind}
            currentToggleLabel={currentToggleLabel}
            isFirst={idx === 0}
            isLast={idx === sorted.length - 1}
          />
        ))}
        {adding && (
          <TimelineItemForm
            kind={kind}
            currentToggleLabel={currentToggleLabel}
            onSaved={() => setAdding(false)}
            onCancel={() => setAdding(false)}
          />
        )}
        {!adding && sorted.length === 0 && (
          <p className="text-sm text-muted-foreground italic">{t("specialist.timeline.empty")}</p>
        )}
      </div>
    </section>
  );
}
