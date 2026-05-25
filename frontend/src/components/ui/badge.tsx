import * as React from "react";
import { cn } from "@/lib/utils";

const tones: Record<string, string> = {
  default: "bg-muted text-foreground",
  primary: "bg-primary text-primary-foreground",
  outline: "border border-input",
  success: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  warning: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  destructive: "bg-destructive/15 text-destructive",
};

export function Badge({
  className,
  tone = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: keyof typeof tones }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
