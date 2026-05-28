import * as React from "react";
import { cn } from "@/lib/utils";

// Monochrome wrapper around the native <select>. Intentional: the Telegram
// WebView renders the native picker as a system sheet, which is a much better
// mobile UX than a custom Radix dropdown.
export const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...props }, ref) => (
  <select
    ref={ref}
    className={cn(
      "flex h-10 w-full appearance-none rounded-md border border-input bg-transparent px-3 py-2 pr-8 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
      // Inline chevron via background-image so we don't pull in an icon dep.
      "bg-[length:14px_14px] bg-[right_0.6rem_center] bg-no-repeat",
      "bg-[image:url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 20 20%22 fill=%22%23737373%22><path d=%22M5.23 7.21a.75.75 0 0 1 1.06.02L10 11.06l3.71-3.83a.75.75 0 1 1 1.08 1.04l-4.25 4.39a.75.75 0 0 1-1.08 0L5.21 8.27a.75.75 0 0 1 .02-1.06z%22/></svg>')]",
      className,
    )}
    {...props}
  >
    {children}
  </select>
));
Select.displayName = "Select";
