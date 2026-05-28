import { useMemo, useState } from "react";
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
import { cn } from "@/lib/utils";

interface ServicesEditorProps {
  primaryCategory: string;
  /** The specialist's currently-selected services (with prices). */
  selected: SpecialistService[];
  onSaved: () => void;
}

/**
 * Edit-mode editor for the Services & Work Conditions section.
 *
 * - The specialist's primary category is rendered first, always expanded.
 * - All other categories live under an "Other categories" accordion that's
 *   collapsed by default.
 * - Each service has a checkbox + price input.
 * - Hitting "Save services" PUTs all checked services to the backend in one
 *   replace-all request.
 */
export function ServicesEditor({
  primaryCategory,
  selected,
  onSaved,
}: ServicesEditorProps) {
  const catalogQuery = useServiceCatalog();
  const save = useReplaceMyServices();
  const [err, setErr] = useState<string | null>(null);

  // Use server catalog if loaded, else the static mirror so the editor renders
  // without waiting for a round-trip on the first paint.
  const catalog = catalogQuery.data ?? SERVICE_CATALOG.map((e, i) => ({ ...e, id: `mirror-${i}`, position: i }));

  // Editable state: slug -> price string. Pre-populated from `selected`.
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
      setErr((e as Error).message);
    }
  }

  return (
    <div className="space-y-4">
      {primary && (
        <CategoryBlock
          label={primary.category}
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
            <AccordionTrigger className="font-medium">Other categories</AccordionTrigger>
            <AccordionContent className="space-y-4 pt-2">
              {others.map((g) => (
                <CategoryBlock
                  key={g.category}
                  label={g.category}
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
        {save.isPending ? "Saving…" : "Save services"}
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
  // Subcategories always collapsible. Primary category sits inside a "block"
  // that's not itself collapsible — its subcategories collapse individually.
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
                        <span className="text-xs text-muted-foreground">$</span>
                        <Input
                          type="number"
                          inputMode="decimal"
                          min={0}
                          placeholder="0"
                          value={priced[item.slug] ?? ""}
                          onChange={(e) => onPrice(item.slug, e.target.value)}
                          disabled={!isSelected}
                          aria-label={`Price for ${item.label}`}
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
