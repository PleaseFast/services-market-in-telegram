import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  useReplaceMyServices,
  useServiceCatalog,
} from "@/features/specialist/api";
import { groupCatalog, SERVICE_CATALOG } from "@/lib/serviceCatalog";
import type { SpecialistService } from "@/features/projects/types";
import { categoryLabel } from "@/lib/categories";
import { ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";

interface ServicesEditorProps {
  primaryCategory: string;
  selected: SpecialistService[];
  onSaved: () => void;
}

export function ServicesEditor({
  primaryCategory,
  selected,
  onSaved,
}: ServicesEditorProps) {
  const { t } = useTranslation();
  const catalogQuery = useServiceCatalog();
  const save = useReplaceMyServices();
  const [err, setErr] = useState<string | null>(null);

  const catalog = catalogQuery.data ?? SERVICE_CATALOG.map((e, i) => ({ ...e, id: `mirror-${i}`, position: i }));

  const [priced, setPriced] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    for (const s of selected) init[s.slug] = s.price_amount;
    return init;
  });

  const grouped = useMemo(() => groupCatalog(catalog), [catalog]);
  const primary = grouped.find((g) => g.category === primaryCategory);
  const others = grouped.filter((g) => g.category !== primaryCategory);

  function toggle(slug: string, checked: boolean) {
    setPriced((prev) => {
      const next = { ...prev };
      if (checked) next[slug] = next[slug] ?? "0";
      else delete next[slug];
      return next;
    });
  }

  function setPrice(slug: string, raw: string) {
    setPriced((prev) => ({ ...prev, [slug]: raw }));
  }

  async function handleSave() {
    setErr(null);
    const items = Object.entries(priced).map(([slug, price]) => ({
      slug,
      price_amount: price || "0",
    }));
    try {
      await save.mutateAsync(items);
      onSaved();
    } catch (e: unknown) {
      setErr(e instanceof ApiError ? e.localized() : (e as Error).message);
    }
  }

  return (
    <div className="space-y-4">
      {primary && (
        <CategoryBlock
          label={categoryLabel(primary.category)}
          subcategories={primary.subcategories}
          priced={priced}
          onToggle={toggle}
          onPrice={setPrice}
          alwaysOpen
        />
      )}

      {others.length > 0 && (
        <Accordion type="single" collapsible>
          <AccordionItem value="other-categories">
            <AccordionTrigger className="font-medium">
              {t("specialist.services.otherCategories")}
            </AccordionTrigger>
            <AccordionContent className="space-y-4 pt-2">
              {others.map((g) => (
                <CategoryBlock
                  key={g.category}
                  label={categoryLabel(g.category)}
                  subcategories={g.subcategories}
                  priced={priced}
                  onToggle={toggle}
                  onPrice={setPrice}
                />
              ))}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}

      {err && <p className="text-sm text-destructive">{err}</p>}
      <Button
        type="button"
        onClick={handleSave}
        disabled={save.isPending}
        className="h-11"
      >
        {save.isPending ? t("specialist.services.saving") : t("specialist.services.save")}
      </Button>
    </div>
  );
}

function CategoryBlock({
  label,
  subcategories,
  priced,
  onToggle,
  onPrice,
  alwaysOpen,
}: {
  label: string;
  subcategories: { subcategory: string; items: { slug: string; label: string }[] }[];
  priced: Record<string, string>;
  onToggle: (slug: string, checked: boolean) => void;
  onPrice: (slug: string, value: string) => void;
  alwaysOpen?: boolean;
}) {
  const { t } = useTranslation();
  return (
    <div className={cn("space-y-2", alwaysOpen ? "" : "pl-2")}>
      <p className="text-sm font-semibold">{label}</p>
      <Accordion type="multiple" defaultValue={alwaysOpen ? subcategories.map((s) => s.subcategory) : []}>
        {subcategories.map((s) => (
          <AccordionItem key={s.subcategory} value={s.subcategory}>
            <AccordionTrigger className="text-sm">{s.subcategory}</AccordionTrigger>
            <AccordionContent>
              <ul className="space-y-2">
                {s.items.map((item) => {
                  const isSelected = item.slug in priced;
                  return (
                    <li
                      key={item.slug}
                      className="flex items-center gap-3 min-h-[44px]"
                    >
                      <input
                        type="checkbox"
                        id={`svc-${item.slug}`}
                        className="h-5 w-5 rounded border-input"
                        checked={isSelected}
                        onChange={(e) => onToggle(item.slug, e.target.checked)}
                      />
                      <label
                        htmlFor={`svc-${item.slug}`}
                        className="flex-1 text-sm cursor-pointer"
                      >
                        {item.label}
                      </label>
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-muted-foreground">
                          {t("specialist.services.currencyHint")}
                        </span>
                        <Input
                          type="number"
                          inputMode="decimal"
                          min={0}
                          placeholder="0"
                          value={priced[item.slug] ?? ""}
                          onChange={(e) => onPrice(item.slug, e.target.value)}
                          disabled={!isSelected}
                          aria-label={t("specialist.services.priceFor", { label: item.label })}
                          className="w-24"
                        />
                      </div>
                    </li>
                  );
                })}
              </ul>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}
