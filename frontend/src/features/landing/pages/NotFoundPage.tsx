import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  const { t } = useTranslation();
  return (
    <div className="py-24 text-center space-y-5">
      <h1 className="text-5xl font-semibold tracking-tight">{t("notFound.title")}</h1>
      <p className="text-muted-foreground">{t("notFound.subtitle")}</p>
      <Button asChild>
        <Link to="/">{t("notFound.back")}</Link>
      </Button>
    </div>
  );
}
