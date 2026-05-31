import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface GuestPromptProps {
  /** Translation key under ``guestPrompt.actions`` (e.g. ``apply``). */
  actionKey?: keyof typeof ACTIONS;
}

const ACTIONS = {
  apply: true,
  openChat: true,
  publish: true,
  leaveReview: true,
} as const;

export function GuestPrompt({ actionKey }: GuestPromptProps) {
  const { t } = useTranslation();
  const action = actionKey
    ? t(`guestPrompt.actions.${actionKey}`)
    : t("guestPrompt.defaultAction");
  return (
    <Card className="border-primary/40">
      <CardHeader>
        <CardTitle>{t("guestPrompt.title")}</CardTitle>
        <CardDescription>{t("guestPrompt.subtitle", { action })}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-2">
        <Button asChild>
          <Link to="/register">{t("guestPrompt.signUp")}</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/login">{t("guestPrompt.signIn")}</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
