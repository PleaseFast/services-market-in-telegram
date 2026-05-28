import type { SpecialistService } from "@/features/projects/types";

interface ServicesBlockProps {
  services: SpecialistService[];
}

/** Read-mode view of services grouped by category > subcategory with prices. */
export function ServicesBlock({ services }: ServicesBlockProps) {
  if (!services || services.length === 0) {
    return (
      <p className="text-sm text-muted-foreground italic">No services listed yet.</p>
    );
  }

  // Group by category > subcategory preserving the order returned by the API.
  const grouped: Map<string, Map<string, SpecialistService[]>> = new Map();
  for (const s of services) {
    if (!grouped.has(s.category)) grouped.set(s.category, new Map());
    const subs = grouped.get(s.category)!;
    if (!subs.has(s.subcategory)) subs.set(s.subcategory, []);
    subs.get(s.subcategory)!.push(s);
  }

  return (
    <div className="space-y-6">
      {Array.from(grouped.entries()).map(([category, subs]) => (
        <div key={category} className="space-y-3">
          <h4 className="text-sm font-semibold">{category}</h4>
          {Array.from(subs.entries()).map(([subcategory, items]) => (
            <div key={subcategory} className="space-y-1">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">
                {subcategory}
              </p>
              <ul className="space-y-1">
                {items.map((s) => (
                  <li
                    key={s.service_id}
                    className="flex items-center justify-between gap-2 text-sm"
                  >
                    <span>{s.label}</span>
                    <span className="font-medium">
                      {Number(s.price_amount).toLocaleString(undefined, {
                        maximumFractionDigits: 2,
                      })}{" "}
                      {s.price_currency}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
